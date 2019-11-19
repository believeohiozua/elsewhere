
https://developer.flutterwave.com/discuss/5d9dfcd96f9a59001ae754fa
class PaymentView(View):
def get(self, args, *kwargs):
form = RaveForm()
context = {'form':form}
return render(self.request, 'rave/makerave.html', context)

def post(self, *args, **kwargs):
    form = RaveForm(self.request.POST)
    cart = Cart.objects.filter(user=self.request.user, ordered=False)
    if cart[0]:
        if form.is_valid():
            payload = {
            "phonenumber": form.cleaned_data.get('phonenumber'),
            "firstname": "temi",
            "lastname": "desola",
            "cardno": form.cleaned_data.get('cardno'),
            "cvv": form.cleaned_data.get('cvv'),
            "expirymonth": form.cleaned_data.get('expirymonth'),
            "expiryyear": form.cleaned_data.get('expiryyear'),
            "amount": int(cart[0].get_total()),
            "email": self.request.user.email,
            "IP": "355426087298442",
                }

            try:
                res = rave.Card.charge(payload)

                if res["suggestedAuth"]:
                    arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])

                    if arg == "pin":
                        Misc.updatePayload(res["suggestedAuth"], payload, pin=form.cleaned_data.get('pin'))
                    if arg == "address":
                        Misc.updatePayload(res["suggestedAuth"], payload, address= {
                            "billingzip": "07205",
                            "billingcity": "Hillside",
                            "billingaddress": "470 Mundet PI",
                            "billingstate": "NJ",
                            "billingcountry": "US"
                            })

                    res = rave.Card.charge(payload)

                if res["validationRequired"]:
                    rave.Card.validate(res["flwRef"], "")

                res = rave.Card.verify(res["txRef"])
                print(res["transactionComplete"])
                messages.info(self.request, "Transaction Complete")

            except RaveExceptions.CardChargeError as e:
                print(e.err["errMsg"])
                print(e.err["flwRef"])
                messages.info(self.request, "Card Charge Error")

            except RaveExceptions.TransactionValidationError as e:
                print(e.err)
                print(e.err["flwRef"])
                messages.info(self.request, "Transaction Validation Error")

            except RaveExceptions.TransactionVerificationError as e:
                print(e.err["errMsg"])
                print(e.err["txRef"])
                messages.info(self.request, "Transaction Verification Error")
    else:
        messages.info(self.request, "No Cart")
    return render(self.request, 'rave/ravepay.html', {'form':form})