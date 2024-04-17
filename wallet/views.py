from django.shortcuts import render,redirect
from order.models import Wallet,Transaction
from django.conf import settings
import json
import razorpay
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import transaction
from django.http import JsonResponse,HttpResponseBadRequest
from django.contrib import messages
from store.models import User
from order.models import Wallet


def wallet(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user, defaults={'balance': 0})
    transactions = Transaction.objects.filter(wallet=wallet).all().order_by('-id')
    context = {'wallet': wallet, 'transactions': transactions}
    
    
    return render(request, 'profile/wallet.html', context)


@csrf_exempt
def paymenthandler2(request):
    if request.method == "POST":
        try:
            # Extract payment details from the POST request
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            print(razorpay_order_id,payment_id,signature)

            # dictionary of payment parameters
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            result = client.utility.verify_payment_signature(params_dict)

            if result:
                amount = int(request.POST.get('amount'))
                user_id = request.POST.get('user_id')
                user = User.objects.get(user_id=user_id)
                wallet = Wallet.objects.get(user=user)
                wallet.balance += amount
                wallet.save()
                Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='CREDIT')
                messages.success(request, f"₹{amount} has been credited to the wallet!")
                return redirect('store:wallet')  
            else:
                return render(request, 'profile/paymentfail.html')
        
        except Exception as e:
            print('Exception:', str(e))
            return redirect('store:payment_failed')  

    else:
        return redirect('store:index')
    
# def payment_failed(request):
#     return render(request, 'profile/paymentfail.html')