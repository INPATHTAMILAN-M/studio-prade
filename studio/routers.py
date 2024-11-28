# urls.py
from rest_framework.routers import DefaultRouter
from account.routers import router as account_router
from postapp.routers import router as post_router


router = DefaultRouter()

router.registry.extend(account_router.registry)
