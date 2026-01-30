import stripe
from fiat.stripe_pay.dist import scrtsxx
stripe.api_key=scrtsxx.SECRET_KEY


class StripePayments():
    def generate_card_token(self, cardnumber,expmonth,expyear,cvv):
        data= stripe.Token.create(
                card={
                    "number": str(cardnumber),
                    "exp_month": int(expmonth),
                    "exp_year": int(expyear),
                    "cvc": str(cvv),
                })
        card_token = data['id']
    
        return card_token
    
    
    def create_payment_charge(self, tokenid,amount):
    
        payment = stripe.Charge.create(
                    amount= int(float(amount)*100),                  # convert amount to cents
                    currency='usd',
                    description='dVPN Credits',
                    source=tokenid,
                    )
    
        payment_check = payment    # return True for payment
    
        return payment_check
    