from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from datetime import datetime
from .serializers import TransactionSerializer
from .models import Account, Transaction

def exchange(_, currencyFrom, amountFrom, currencyTo):
    # Converting to floats
    try:
        amountFrom = float(amountFrom)
    except ValueError:
        return HttpResponseBadRequest('Invalid amount')
    
    # Making an API request to exchange
    response = requests.get(f'https://api.freecurrencyapi.com/v1/latest?apikey=tbSPK9nG61DqLzffT04z52YoaCd7cL9FGUypps8B&currencies={currencyTo}&base_currency={currencyFrom}')

    if response.status_code == 200:
        data = response.json()

        # Converting the currency
        rate = data['data'][currencyTo]

        convertedCurrency = amountFrom * rate

        return JsonResponse({'convertedAmount': convertedCurrency})
    else:
        return JsonResponse({'message': 'Request failed'})

@csrf_exempt
def pay(request):
    if (request.method == 'POST'):
        body = request.body.decode('utf-8')
        data = json.loads(body)

        amount = data.get('amount')
        companyName = data.get('companyName')

        try:
            amount = float(amount)
        except ValueError:
            return HttpResponseBadRequest('Invalid amount')

        try:
            foundAccount = Account.objects.get(companyName=companyName)
        except foundAccount.DoesNotExist:
            return HttpResponseNotFound({'message': 'The recipient account is missing'})
        
        foundAccount.balance = foundAccount.balance + amount

        foundAccount.save()

        now = datetime.now()

        data = {
            'companyName': companyName, 
            'date': now, 
            'amount': amount,
            'status': True,
        }

        serializer = TransactionSerializer(data = data)

        if serializer.is_valid():
            transaction = serializer.save()
            return JsonResponse({'status': True, 'transactionId': transaction.id})
        
        return HttpResponseNotFound({'Failed to create a transaction'})
        

@csrf_exempt
def refund(request):
    if (request.method == 'POST'):
        body = request.body.decode('utf-8')
        data = json.loads(body)

        transactionId = data.get('transactionId')
        reservationId = data.get('reservationId')

        try:
            transactionId = float(transactionId)
        except ValueError:
            return HttpResponseBadRequest('Invalid transactionId')
        
        try:
            foundTransaction = Transaction.objects.get(id = transactionId)
        except foundTransaction.DoesNotExist:
            return HttpResponseNotFound({'message': 'The recipient account is missing'})
        
        try:
            foundAccount = Account.objects.get(companyName = foundTransaction.companyName)
        except foundAccount.DoesNotExist:
            return HttpResponseNotFound({'message': 'The recipient account is missing'})
        
        foundAccount.balance = foundAccount.balance - foundTransaction.amount
        foundTransaction.status = False

        foundTransaction.save()
        foundAccount.save()

        payload = {'fields':{'ReservationID': reservationId}}
        response = requests.post('http://127.0.0.1:8000/airline/cancel_booking',json=payload)
        data = response.json()

        if data.Status == True:
            return JsonResponse({'status': True})
        
    return JsonResponse({'status': True})

