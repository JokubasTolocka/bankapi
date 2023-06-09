from django.http import JsonResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from datetime import datetime
from .serializers import TransactionSerializer
from .models import Account, Transaction

def exchange(_, currencyFrom, amountFrom):
    # Converting to floats
    try:
        amountFrom = float(amountFrom)
    except ValueError:
        return JsonResponse({'status': 'failed', 'message': 'Invalid amount'})

    currencies = {
        'GBP': 1,
        'USD': 1.25,
        'EUR': 1.14,
        'JPY': 168.22,
        'AUD': 1.86,
        'CAD': 1.68,
        'CHF': 1.11,
        'CNY': 8.71,
        'SEK': 12.91,
        'NZD': 1.98,
    }

    try: 
        convertedCurrency = amountFrom / currencies[currencyFrom]
    except KeyError:
        return JsonResponse({'status': 'failed', 'message': 'Cannot convert from this currency'})

        
    
    return JsonResponse({'status': 'success', 'convertedAmount': convertedCurrency})

@csrf_exempt
def pay(request):
    if (request.method == 'POST'):
        data = json.loads(request.body)

        amount = data.get('amount')
        companyName = data.get('companyName')
        bookingID = data.get('bookingID')

        try:
            amount = float(amount)
        except ValueError:
            return JsonResponse({'status': 'failed', 'message': 'Invalid amount'})

        try:
            foundAccount = Account.objects.get(companyName=companyName)
        except foundAccount.DoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Cannot get account'})
        
        foundAccount.balance = foundAccount.balance + amount

        foundAccount.save()

        now = datetime.now()

        data = {
            'companyName': companyName, 
            'bookingID': bookingID,
            'date': now, 
            'amount': amount,
            'status': True,
        }
        
        serializer = TransactionSerializer(data = data)

        if serializer.is_valid():
            transaction = serializer.save()

            airlineIndicator = bookingID[:2]

            airlines = {
                "00": "ed19km2b",
                "01": "mavericklow",
                "02": "krzsztfkml",
                "03": "safwanchowdhury",
            }

            payload = {'bookingID': str(bookingID), "amount": amount}
            response = requests.post(f'https://{airlines[airlineIndicator]}.pythonanywhere.com/airline/confirm_booking', json=payload)
            data = response.json()

            if data.get("status") == "success":
                return JsonResponse({'status': "success", 'transactionId': transaction.id})
            
            if data.get("status") == "failed":
                return JsonResponse({'status': "failed", "message": "failed to confirm booking"})
        
        return JsonResponse({'status': "failed"})
        

@csrf_exempt
def refund(request):
    if (request.method == 'POST'):
        data = json.loads(request.body)

        bookingID = data.get('bookingID')

        try:
            foundTransaction = Transaction.objects.get(bookingID = bookingID)
        except:
            return JsonResponse({'status': "failed", 'message': 'The transaction is missing'})
        
        try:
            foundAccount = Account.objects.get(companyName = foundTransaction.companyName)
        except foundAccount.DoesNotExist:
            return JsonResponse({'status': "failed", 'message': 'The recipient account is missing'})
        
        foundAccount.balance = foundAccount.balance - foundTransaction.amount
        foundTransaction.status = False

        foundTransaction.save()
        foundAccount.save()

        airlineIndicator = bookingID[:2]

        airlines = {
            "00": "ed19km2b",
            "01": "mavericklow",
            "02": "krzsztfkml",
            "03": "safwanchowdhury",
        }

        payload = {'bookingID': str(bookingID)}
        response = requests.post(f'https://{airlines[airlineIndicator]}.pythonanywhere.com/airline/cancel_booking', json=payload)
        data = response.json()

        if data.get("status") == "success":
            return JsonResponse({'status': "success"})
        
        if data.get("status") == "failed":
            return JsonResponse({'status': "failed", "message": "failed to cancel booking on airline"})
        
    return JsonResponse({'status': "failed"})

