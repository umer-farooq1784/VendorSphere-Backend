from django.test import TestCase
from django.urls import path
from main.views.user import NormalUserList
from main.views.user import NormalUserDetail
from main.views.user import update_profile
from main.views.user import login_view
from main.views.user import signup_view
from main.views.user import logout_view
from main.views.product import ProductList
from main.views.product import ProductDetail
from main.views.product import add_product
from main.views.product import searchProducts
from main.views.category import category_names
from main.views.store import add_store , searchStores
from main.views.product import get_top_products
from main.views.product import add_product_review
from main.views.store import add_store_review
from main.views.store import get_store_reviews
from main.views.product import get_product_reviews
from main.views.product import get_product_details
from main.views.product import my_product_catalog
from main.views.product import update_product
from main.views.product import feature_product
from main.views.product import get_featured_products
from main.views.store import my_store_catalog
from main.views.store import get_store_details
from main.views.store import get_top_stores
from main.views.store import feature_store
from main.views.store import update_store
from main.views.store import get_featured_stores
from main.views.email import send_email
from main.views.user import delete_account
from main.views.payment import create_payment_intent
from main.views.contract import send_contract_view
from main.views.contract import accept_contract_view
from main.views.contract import reject_contract_view
from main.views.contract import UserContractsView
from main.views.contract import PendingContractsView
from main.views.contract import StoreInventoryView
from main.views.contract import user_contracts_view
from main.views.contract import single_contract_view
from main.views.contract import check_accepted_contract_product
from main.views.contract import check_accepted_contract_store
from main.views.inventory import get_user_inventory
from main.views.inventory import inventory_detail
from main.views.inventory import decrement_inventory
from main.views.inventory import increment_inventory
from main.views.user  import update_subscription
#from main.views.sales import get_sales
from main.views.contract import check_active_contracts
from main.views.contract import check_expired_contracts
from main.views.sales import get_prices_by_id
from main.views.sales import get_percentage
from main.views.sales import totalProduct
from main.views.sales import totalSales
from main.views.product import Setfeature_product
from main.views.store import Setfeature_store
from main.views.reports import report_user
from main.views.contract import get_not_already_existing_product_contract

urlpatterns = [
    path("users/", NormalUserList.as_view()),
    path("users/<int:pk>/", NormalUserDetail.as_view()),
    path("updateProfile/", update_profile, name="update_profile"),
    path("product/", ProductList.as_view()),
    path("product/<int:pk>/", ProductDetail.as_view()),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("add_product/", add_product, name="add_product"),
    path("logout/", logout_view, name="logout"),
    path("categories/", category_names, name="casignuptogies_view"),
    path("add_store/", add_store, name="add_store"),
    path("get_top_products/", get_top_products, name="get_top_products"),
    path("searchstores/", searchStores, name="search"),
    path("searchproducts/", searchProducts, name="search"),
    path(
        "add_product_review/<int:product_id>/",
        add_product_review,
        name="add_product_review",
    ),
    path("add_store_review/<int:store_id>/", add_store_review, name="add_store_review"),
    path(
        "get_product_reviews/<int:product_id>/",
        get_product_reviews,
        name="get_product_reviews",
    ),
    path(
        "get_store_reviews/<int:store_id>/",
        get_store_reviews,
        name="get_store_reviews",
    ),
    path("get_product_details/<int:product_id>/", get_product_details, name="get_product_details"),
    path("my_product_catalog/<int:user_id>/", my_product_catalog, name="my_product_catalog"),
    path("my_store_catalog/<int:user_id>/", my_store_catalog, name="my_store_catalog"),
    path("get_store_details/<int:store_id>/", get_store_details, name="get_store_details"),
    path("get_top_stores/", get_top_stores, name="get_top_stores"),
    path("email/",send_email,name="send_email"),
    path("delete_account/", delete_account, name="delete_account"),
    path('subscription/', update_subscription, name='update_subscription'),
    path("process_payment/",create_payment_intent, name="process_payment"),
    path('store/<int:store_id>/inventory/', StoreInventoryView.as_view(), name='store-inventory'),
    path('contract/send/', send_contract_view, name='send-contract'),
    path('contract/accept/', accept_contract_view, name='accept-contract'),
    path('contract/reject/', reject_contract_view, name='reject-contract'),
    path('user/<int:user_id>/contracts/', UserContractsView.as_view(), name='user-contracts'),
    path('user/<int:user_id>/pending-contracts/', PendingContractsView.as_view(), name='pending-contracts'),
    path('contracts/<int:user_id>/', user_contracts_view, name='user_contracts'),
    path('contract/<int:contract_id>/', single_contract_view, name='single-contract'),
    path('user/<int:user_id>/inventory/', get_user_inventory, name='user_inventory'),
    path('inventory/<int:inventory_id>/', inventory_detail, name='inventory_detail'),
    path('inventory/<int:inventory_id>/decrement/', decrement_inventory, name='decrement_inventory'),
    path('inventory/<int:inventory_id>/increment/', increment_inventory, name='increment_inventory'),
    path("feature_store/<int:store_id>/", feature_store, name="feature_store"),
    path("feature_product/<int:product_id>/", feature_product, name="feature_product"),
    path("get_featured_products/", get_featured_products, name="get_featured_products"),
    path("get_featured_stores/", get_featured_stores, name="get_featured_stores"),
    path("update_product/<int:product_id>/", update_product, name="update_product"),
    path("update_store/<int:store_id>/", update_store, name="update_store"),
#    path('sales/by-email/<str:email>/', get_sales, name='get_sales'),
    path('check_active_records/<int:user_id>/', check_active_contracts, name='check_active_records'),
    path('check_expire_records/<int:user_id>/', check_expired_contracts, name='check_active_records'),
    path('contract/check_product/<int:product_id>/<int:user_id>/', check_accepted_contract_product, name='check_accepted_contract_product'),
    path('contract/check_store/<int:store_id>/<int:user_id>/', check_accepted_contract_store, name='check_accepted_contract_store'),
    path('sales/prices/<int:id>/', get_prices_by_id, name='get_prices_by_id'),
    path('get_percentage/<int:id>/', get_percentage, name='get_percentage'),
    path('totalproduct/<int:id>/', totalProduct, name='totalProduct'),
    path('totalsales/<int:id>/', totalSales, name='totalSales'),
    path('feature_store/', Setfeature_store, name='featurestore/product'),
    path('feature_product/', Setfeature_product, name='featurestore/product'),
    path('report_user/', report_user, name='report_user'),
    path('get_not_already_existing_product_contract/<int:product_id>/<int:user_id>/', get_not_already_existing_product_contract, name='get_not_already_existing_product_contract'),
]
