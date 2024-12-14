# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

#Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

#Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")
            first_name = data.get("firstName")
            last_name = data.get("lastName")
            email = data.get("email")

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already exists"}, status=400)

            # Create the user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            # Log the user in
            login(request, user)

            # Return a JSON response with user details
            response_data = data = {"userName":username,"status":"Authenticated"}
            return JsonResponse(response_data, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
def get_dealerships(request):
    try:
        # Fetch all dealerships from the database
        dealerships = Dealership.objects.all()
        
        # Convert the dealerships queryset to a list of dictionaries (serializing)
        dealerships_list = list(dealerships.values())
        
        # Return the dealerships as a JSON response
        return JsonResponse({"status": 200, "dealerships": dealerships_list})
    
    except Exception as e:
        return JsonResponse({"status": 500, "message": str(e)})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `add_review` view to submit a review
def add_review(request):
    # Check if the request is a POST request
    if request.method == 'POST':
        try:
            # Extract data from the POST request
            name = request.POST.get('name')
            dealership_id = request.POST.get('dealership')
            review_text = request.POST.get('review')
            purchase = request.POST.get('purchase') == 'true'  # Convert to boolean
            purchase_date = request.POST.get('purchase_date')
            car_make = request.POST.get('car_make')
            car_model = request.POST.get('car_model')
            car_year = request.POST.get('car_year')

            # Parse the purchase date if it's provided
            if purchase_date:
                purchase_date = parse_datetime(purchase_date)
            else:
                purchase_date = None

            # Fetch the dealer object using the dealership ID
            dealer = get_object_or_404(Dealer, id=dealership_id)

            # Create a new Review object
            review = Review.objects.create(
                dealership=dealer,
                name=name,
                review=review_text,
                purchase=purchase,
                purchase_date=purchase_date,
                car_make=car_make,
                car_model=car_model,
                car_year=car_year
            )

            # Return a successful response
            return JsonResponse({
                "status": 201,
                "message": "Review added successfully",
                "review": {
                    "id": review.id,
                    "name": review.name,
                    "dealership": review.dealership.id,
                    "review": review.review,
                    "purchase": review.purchase,
                    "purchase_date": review.purchase_date,
                    "car_make": review.car_make,
                    "car_model": review.car_model,
                    "car_year": review.car_year
                }
            })

        except Exception as e:
            # Handle errors and send back a failed response
            return JsonResponse({"status": 400, "message": str(e)})

    else:
        # Return error if the method is not POST
        return JsonResponse({"status": 400, "message": "Invalid request method"})

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})