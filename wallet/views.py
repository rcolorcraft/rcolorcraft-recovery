from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Wallet, WalletTransaction
import razorpay
import json
import time
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal


# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def wallet_dashboard(request):
    """Display user's wallet balance and transactions"""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.order_by("-created_at")
    return render(request, "dashboard.html", {
        "wallet": wallet,
        "transactions": transactions
    })


@login_required
@csrf_exempt
def create_razorpay_order_wallet(request):
    """Create a Razorpay order for wallet top-up"""
    try:
        amount_str = request.POST.get('amount', '0')
        amount = int(float(amount_str) * 100)  # Convert to paise
        if request.user.role == 'employee' and amount < 20000:
            return JsonResponse({'success': False, 'error': 'Minimum amount is ₹200 for artists/employees.'})
        elif amount < 100:
            return JsonResponse({'success': False, 'error': 'Minimum amount is ₹1'})

        receipt_id = f'wallet_{int(time.time())}'
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': receipt_id,
            'payment_capture': 1
        }

        order = razorpay_client.order.create(data=order_data)
        return JsonResponse({
            'success': True,
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key_id': settings.RAZORPAY_KEY_ID
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
def verify_razorpay_payment_wallet(request):
    """Verify Razorpay payment and credit to wallet"""
    try:
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        amount = Decimal(str(data.get('amount', '0')))

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        print(params_dict)

        # ✅ Verify payment signature
        razorpay_client.utility.verify_payment_signature(params_dict)

        # ✅ Credit the wallet
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.credit(amount)

        # ✅ Log the transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type="CREDIT",
            razorpay_payment_id=razorpay_payment_id
        )

        return JsonResponse({'success': True, 'message': 'Wallet credited successfully'})

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'success': False, 'error': 'Payment signature verification failed'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
