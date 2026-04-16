from django.http import JsonResponse
from django.shortcuts import render
from .models import ServiceImage


def service_images_view(request):
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

            for img in images:
                ServiceImage.objects.create(
                    image_name=name,
                    price=price,
                    min_size=min_size,
                    image=img,
                    type_of_art=type_of_art,
                    userupload_id=user_id,
                    userupload_name=user_name,
                )

            return JsonResponse(
                {"success": True, "message": "✅ Service Image added successfully!"}
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": f"❌ {str(e)}"})

    return render(request, "service_images.html")
