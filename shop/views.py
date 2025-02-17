from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Orders, OrderUpdate
import math
from django.views.decorators.csrf import csrf_exempt
import json
from paytm import Checksum
# Create your views here.
MERCHANT_KEY='kbzk1DSbJiV_O3p5'
def searchMatch(query, item):
    query=query.lower()
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def index(request):
    products= Product.objects.all()
    n= len(products)

    allProds=[]
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    for cat in cats:
      nSlides= n//4 + math.ceil((n/4)-(n//4))
      prod=Product.objects.filter(category=cat)
      allProds.append([prod,range(1,nSlides), nSlides])

    params={'allProds':allProds }
    return render(request,"shop/index.html", params)
def search(request):
    query = request.GET.get('search')
    products= Product.objects.all()
    n= len(products)

    allProds=[]
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    for cat in cats:
      nSlides= n//4 + math.ceil((n/4)-(n//4))
      
      prodtemp=Product.objects.filter(category=cat)
      
      prod=[item for item in prodtemp if searchMatch(query, item)]
      if len(prod)!=0:
        allProds.append([prod,range(1,nSlides), nSlides])

    params={'allProds':allProds, 'msg':"" }
    if len(allProds)==0 or len(query)<4:
        params = {'msg':"Please make sure to enter a relevant search query"}
    return render(request,"shop/index.html", params)

def about (request):
    return render(request,'shop/about.html')

def contact (request):
   thank=False
   if request.method=="POST":
      print(request )
      name=request.POST.get('name', "")
      email=request.POST.get('email',"")
      phone=request.POST.get('phone',"")
      desc=request.POST.get('desc',"")
   
      contact= Contact(name=name, email=email, phone=phone, desc=desc)
      contact.save()
      thank=True
   return render(request,'shop/contact.html',{'thank':thank})

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            print(orderId)
            order = Orders.objects.filter(order_id=orderId, email=email)
            print(len(order))
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                print(len(update))
                updates = []
                
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    print(updates)
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].item _Njson}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"success"}')

    return render(request, 'shop/tracker.html')

    
def prodView (request,myid):
   product=Product.objects.filter(id=myid)
   print (product)
   return render(request,'shop/prodView.html',{'product':product[0]})
   

def checkout (request):
   if request.method=="POST":
      items_json=request.POST.get('itemsJson','')
      name=request.POST.get('name', "")
      amount=request.POST.get('amount', "")
      
      email=request.POST.get('email',"")
      address=request.POST.get('address1',"") + " " + request.POST.get('address2',"")
      city=request.POST.get('city',"")
      state=request.POST.get('state',"")
      zip_code=request.POST.get('zip_code',"")
      phone=request.POST.get('phone',"")
      thank=True
      
      order= Orders(item_json=items_json,name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
      order.save()
      update=OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
      update.save()
      id=order.order_id
      param_dict = {
            'MID':'WorldP64425807474247',
            'ORDER_ID':str(order.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING3231',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/'
        }
      param_dict['CHECKSUMHASH']=Checksum.generate_checksum(param_dict, MERCHANT_KEY)
      return render(request,'shop/paytm.html',{'param_dict':param_dict})
      #request paytm to transfer you the money
   return render(request,'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checks = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checks)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
    
# from paytm import Checksum
# import logging
# from django.shortcuts import render
# from django.http import HttpResponse
# from .models import Product, Contact, Orders, OrderUpdate
# import math
# from django.views.decorators.csrf import csrf_exempt
# import json
# from paytm import Checksum

# logger = logging.getLogger(__name__)

# MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'

# def index(request):
#     allProds = []
#     catprods = Product.objects.values('category', 'id')
#     cats = {item['category'] for item in catprods}
#     for cat in cats:
#         prod = Product.objects.filter(category=cat)
#         n = len(prod)
#         nSlides = n // 4 + ceil((n / 4) - (n // 4))
#         allProds.append([prod, range(1, nSlides), nSlides])
#     params = {'allProds':allProds}
#     return render(request, 'shop/index.html', params)


# def about(request):
#     return render(request, 'shop/about.html')


# def contact(request):
#     thank = False
#     if request.method=="POST":
#         name = request.POST.get('name', '')
#         email = request.POST.get('email', '')
#         phone = request.POST.get('phone', '')
#         desc = request.POST.get('desc', '')
#         contact = Contact(name=name, email=email, phone=phone, desc=desc)
#         contact.save()
#         thank = True
#     return render(request, 'shop/contact.html', {'thank': thank})


# def tracker(request):
#     if request.method=="POST":
#         orderId = request.POST.get('orderId', '')
#         email = request.POST.get('email', '')
#         try:
#             order = Orders.objects.filter(order_id=orderId, email=email)
#             if len(order)>0:
#                 update = OrderUpdate.objects.filter(order_id=orderId)
#                 updates = []
#                 for item in update:
#                     updates.append({'text': item.update_desc, 'time': item.timestamp})
#                     response = json.dumps([updates, order[0].items_json], default=str)
#                 return HttpResponse(response)
#             else:
#                 return HttpResponse('{}')
#         except Exception as e:
#             return HttpResponse('{}')

#     return render(request, 'shop/tracker.html')


# def search(request):
#     return render(request, 'shop/search.html')


# def prodView(request, myid):

#     # Fetch the product using the id
#     product = Product.objects.filter(id=myid)
#     return render(request, 'shop/prodView.html', {'product':product[0]})


# def checkout(request):
#     if request.method=="POST":
#         items_json = request.POST.get('itemsJson', '')
#         name = request.POST.get('name', '')
#         amount = request.POST.get('amount', '')
#         email = request.POST.get('email', '')
#         address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
#         city = request.POST.get('city', '')
#         state = request.POST.get('state', '')
#         zip_code = request.POST.get('zip_code', '')
#         phone = request.POST.get('phone', '')
#         order = Orders(item_json=items_json, name=name, email=email, address=address, city=city,
#                        state=state, zip_code=zip_code, phone=phone, amount=amount)
#         order.save()
#         update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
#         update.save()
#         thank = True
#         id = order.order_id
#         paytmParams = dict()
#         # return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
#         # Request paytm to transfer the amount to your account after payment by user
#         paytmParams["body"] = {
#     "requestType"   : "Payment",
#     "mid"           : 'WorldP64425807474247',
#     "websiteName"   : "WEBSTAGING3231",
#     "orderId"       : str(order.order_id),
#     "callbackUrl"   : "http://127.0.0.1:8000/shop/handlerequest/",
#     "txnAmount"     : {
#         "value"     : str(amount),
#         "currency"  : "INR",
#     },
#     "userInfo"      : {
#         "custId"    : email,
#     },
# }   
#         checksum = Checksum.generateSignature(json.dumps(paytmParams["body"]), "WorldP64425807474247")

#         paytmParams["head"] = {
#             "signature"    : checksum
#         }

#         post_data = json.dumps(paytmParams)

#         # for Staging
#         url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid=WorldP64425807474247&orderId="+str(order.order_id)

#         # for Production
#         # url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"
#         response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
#         print(response)

# #  'MID':'WorldP64425807474247',
# #             'ORDER_ID':str(order.order_id),
# #             'TXN_AMOUNT':str(amount),
# #             'CUST_ID':email,
# #             'INDUSTRY_TYPE_ID':'Retail',
# #             'WEBSITE':'WEBSTAGING3231',
# #             'CHANNEL_ID':'WEB',
# # 	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/'
#         # param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
#         print(param_dict)
#         return render(request, 'shop/paytm.html', {'param_dict': param_dict})

#     return render(request, 'shop/checkout.html')


# @csrf_exempt
# def handlerequest(request):
#     form = request.POST
#     response_dict = {}
#     checksum = None  # Initialize checksum to ensure it's defined
#     print(form)
#     for i in form.keys():
#         response_dict[i] = form[i]
#         if i == 'CHECKSUMHASH':
#             checksum = form[i]  # Assign the checksum value

#     logger.info(f"Received data: {form}")

#     if not checksum:
#         logger.error("Checksum not found in the request")
#         return HttpResponse("Checksum not found in the request", status=400)  # Handle missing checksum case

#     verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
#     if verify:
#         if response_dict['RESPCODE'] == '01':
#             logger.info('Order successful')
#         else:
#             logger.warning(f"Order was not successful because {response_dict['RESPMSG']}")
#     else:
#         logger.error('Checksum verification failed')

#     return render(request, 'shop/paymentstatus.html', {'response': response_dict})