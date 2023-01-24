from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from .models import Order
from .utils import send_email_to_admin


class OrderView(View):
    def get(self, request):
        if request.method == "GET":
            return render(request, 'orders/index.html', {"title": "Onlayn sifariş yerləşdir"})

    def post(self, request):
        # Formdan gelen datalari gotur
        try:
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone')
            order_url = request.POST.get('link')
            notes = request.POST.get('message')

            if name is not None and surname is not None and email is not None and phone_number is not None and \
                    order_url is not None and notes is not None:

                order_obj = Order.objects.create(
                    name=name,
                    surname=surname,
                    email=email,
                    phone_number=phone_number,
                    order_url=order_url,
                    notes=notes)

                order_obj.save()

                send_email_to_admin(order_obj.name,
                                    order_obj.surname,
                                    order_obj.email,
                                    order_obj.phone_number,
                                    order_obj.order_url,
                                    order_obj.notes
                    )
            else:
                return HttpResponse("Datalar boş olmamalıdır!", status=500)

        except:
            return HttpResponse("Görünüşə görə front id-ləri gözlənildiyi kimi deyil!", status=500)
        # Amin, ele et ki, sifarisi doldurub donder vuranda, heqiqten email de gelsin, admin panelde de gorunsun sifaris
        return HttpResponse("Response back!", status=200)
