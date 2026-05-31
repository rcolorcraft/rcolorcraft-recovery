from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import ServiceImage
from django.contrib.auth.decorators import user_passes_test
import os
import subprocess
import tempfile


VIDEO_EXTS = (".mp4", ".mov", ".avi", ".webm", ".mkv", ".m4v")
MAX_PHOTOS = 20
MAX_VIDEOS = 10
MAX_VIDEO_SECONDS = 15


def _media_url(item):
    if item.file_url:
        return str(item.file_url).lower()
    try:
        return str(item.image.url).lower()
    except Exception:
        return str(item.image).lower()


def _is_video_by_name_or_type(uploaded_file):
    content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
    name = (getattr(uploaded_file, "name", "") or "").lower()
    return content_type.startswith("video/") or name.endswith(VIDEO_EXTS)


def _is_video_item(item):
    return _media_url(item).endswith(VIDEO_EXTS)


def _get_video_duration_seconds(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        temp_path = tmp.name
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                temp_path,
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            return None
        return float((result.stdout or "").strip())
    except Exception:
        return None
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass


def service_images_view(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Login required to upload portfolio."},
            status=401,
        )
    if not (request.user.is_staff or getattr(request.user, "role", "") == "employee"):
        return JsonResponse(
            {
                "success": False,
                "message": "Only artist/employee accounts can upload portfolio.",
            },
            status=403,
        )

    if request.method == "POST":
        try:
            name = request.POST.get("image_name")
            price = request.POST.get("price")
            width = request.POST.get("width")
            height = request.POST.get("height")
            min_size = f"{width} * {height}"  # combine
            type_of_art = request.POST.get("type_of_art")
            images = request.FILES.getlist("images")

            user_name = "Anonymous"
            user_id = 0
            if (
                hasattr(request.user, "is_authenticated")
                and request.user.is_authenticated
            ):
                user_id = getattr(request.user, "id", 0)
                user_name = (
                    getattr(request.user, "full_name", None)
                    or getattr(request.user, "email", None)
                    or "Anonymous"
                )

                if request.user.is_staff:
                    approved_status = True
                else:
                    approved_status = False

            # Apply upload limits only for employee role, not admin
            if getattr(request.user, "role", "") == "employee":
                existing_uploads = ServiceImage.objects.filter(userupload_id=user_id)
                existing_photo_count = sum(
                    1 for row in existing_uploads if not _is_video_item(row)
                )
                existing_video_count = sum(
                    1 for row in existing_uploads if _is_video_item(row)
                )

                incoming_photos = []
                incoming_videos = []
                for f in images:
                    if _is_video_by_name_or_type(f):
                        incoming_videos.append(f)
                    else:
                        incoming_photos.append(f)

                if existing_photo_count + len(incoming_photos) > MAX_PHOTOS:
                    remaining = max(0, MAX_PHOTOS - existing_photo_count)
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f"Photo upload limit reached. You can upload only {remaining} more photo(s). Maximum {MAX_PHOTOS} photos allowed.",
                        }
                    )

                if existing_video_count + len(incoming_videos) > MAX_VIDEOS:
                    remaining = max(0, MAX_VIDEOS - existing_video_count)
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f"Video upload limit reached. You can upload only {remaining} more video(s). Maximum {MAX_VIDEOS} videos allowed.",
                        }
                    )

                for vid in incoming_videos:
                    duration = _get_video_duration_seconds(vid)
                    if duration is None:
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "Unable to validate video duration. Please upload a valid video file.",
                            }
                        )
                    if duration > MAX_VIDEO_SECONDS:
                        return JsonResponse(
                            {
                                "success": False,
                                "message": f"Video '{vid.name}' is {duration:.1f}s. Maximum allowed is {MAX_VIDEO_SECONDS}s.",
                            }
                        )
                    vid.seek(0)

            for img in images:
                ServiceImage.objects.create(
                    image_name=name,
                    price=price,
                    min_size=min_size,
                    image=img,
                    type_of_art=type_of_art,
                    userupload_id=user_id,
                    userupload_name=user_name,
                    is_approved=approved_status,  # 👈 ये add करना है
                )

            return JsonResponse(
                {"success": True, "message": "✅ Service Image added successfully!"}
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": f"❌ {str(e)}"})

    return render(request, "service_images.html")


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def pending_uploads_view(request):
    pending_uploads = ServiceImage.objects.filter(is_approved=False).order_by("-id")
    pending_items = []
    for item in pending_uploads:
        media_url = _media_url(item)
        pending_items.append(
            {
                "obj": item,
                "is_video": _is_video_item(item),
                "media_url": media_url,
            }
        )
    return render(
        request,
        "employee/pending_uploads.html",
        {"pending_uploads": pending_uploads, "pending_items": pending_items},
    )
