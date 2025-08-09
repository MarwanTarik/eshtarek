from tokenize import TokenError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .permissions import IsAdmin, IsTenantAdmin, IsAdminOrTenantAdmin
from .serializers import *
from .enums.subscriptions_status import SubscriptionsStatus

# Create your views here.
class UserRegistrationView(APIView):    
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                token_serializer = CustomTokenObtainPairSerializer()
                refresh = token_serializer.get_token(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TenantRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = TenantRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                token_serializer = CustomTokenObtainPairSerializer()
                refresh = token_serializer.get_token(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = AdminRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                token_serializer = CustomTokenObtainPairSerializer()
                refresh = token_serializer.get_token(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST) 


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Successfully logged out"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except TokenError as e:
            return Response(
                {"error": "refresh token is invalid or expired"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = CustomTokenObtainPairSerializer(data=request.data)
            
            if serializer.is_valid():
                token_data = serializer.validated_data
                return Response(token_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class PlanView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        try: 
            serializer = PlanSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                plan = serializer.save()
                plan = Plans.objects.prefetch_related(
                    'plan_limit_policies__limit_policy'
                ).get(pk=plan.pk)
                return Response(PlanSerializer(plan).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request, pk=None):
        try:
            if pk:
                
                plan = Plans.objects.prefetch_related(
                    'plan_limit_policies__limit_policy'
                ).get(pk=pk)
                
                serializer = PlanSerializer(plan)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                plans = Plans.objects.prefetch_related(
                    'plan_limit_policies__limit_policy'
                ).all()
                serializer = PlanSerializer(plans, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Plans.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            plan = Plans.objects.prefetch_related(
                'plan_limit_policies__limit_policy'
            ).get(pk=pk)
            serializer = PlanSerializer(plan, data=request.data, partial=True)
            if serializer.is_valid():
                updated_plan = serializer.save()
                updated_plan = Plans.objects.prefetch_related(
                    'plan_limit_policies__limit_policy'
                ).get(pk=updated_plan.pk)
                return Response(PlanSerializer(updated_plan).data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Plans.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            plan = Plans.objects.get(pk=pk)
        except Plans.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        
        plan.delete()
        return Response({"message": "Plan deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class LimitPoliciesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        try:
            serializer = LimitPoliciesSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                limit_policy = serializer.save()
                return Response(LimitPoliciesSerializer(limit_policy).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        try:
            if pk:
                limit_policy = LimitPolicies.objects.get(pk=pk)
                
                serializer = LimitPoliciesSerializer(limit_policy)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                limit_policies = LimitPolicies.objects.all()
                serializer = LimitPoliciesSerializer(limit_policies, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except LimitPolicies.DoesNotExist:
            return Response({"error": "Limit policy not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            limit_policy = LimitPolicies.objects.get(pk=pk)
        except LimitPolicies.DoesNotExist:
            return Response({"error": "Limit policy not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LimitPoliciesSerializer(limit_policy, data=request.data, partial=True)
        if serializer.is_valid():
            updated_limit_policy = serializer.save()
            return Response(LimitPoliciesSerializer(updated_limit_policy).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            limit_policy = LimitPolicies.objects.get(pk=pk)
        except LimitPolicies.DoesNotExist:
            return Response({"error": "Limit policy not found"}, status=status.HTTP_404_NOT_FOUND)
        
        limit_policy.delete()
        return Response({"message": "Limit policy deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
 
class PlanLimitPolicyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request):
        try:
            plan_id = request.data.get('plan_id')
            policy_id = request.data.get('policy_id')
            plan_limit_policy = PlansLimitPolicies.objects.get(plan_id=plan_id, limit_policy_id=policy_id)
        except PlansLimitPolicies.DoesNotExist:
            return Response({"error": "Plan limit policy not found"}, status=status.HTTP_404_NOT_FOUND)
        
        plan_limit_policy.delete()
        return Response({"message": "Plan limit policy deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

    def post(self, request):
        try:
            serializer = PlanLimitPolicySerializer(data=request.data)
            if serializer.is_valid():
                plan_limit_policy = serializer.save()
                return Response(PlanLimitPolicySerializer(plan_limit_policy).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrTenantAdmin]

    def post(self, request):
        if not request.user.role == Role.TENANT_ADMIN.value:
            return Response({"error": "Only tenant admins can create subscriptions."}, status=status.HTTP_403_FORBIDDEN)    
        try:
            serializer = SubscriptionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                subscription = serializer.save()
                return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        try:
            if pk:
                subscription = Subscriptions.objects.get(pk=pk)
                
                serializer = SubscriptionSerializer(subscription)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                subscriptions = Subscriptions.objects.all()
                serializer = SubscriptionSerializer(subscriptions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Subscriptions.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            subscription = Subscriptions.objects.get(pk=pk)
    
            serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)
            if serializer.is_valid():
                updated_subscription = serializer.save()
                return Response(SubscriptionSerializer(updated_subscription).data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Subscriptions.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, pk):
        try:
            subscription = Subscriptions.objects.get(pk=pk)
            new_subscription_status = SubscriptionsStatus.CANCELLED
            subscription.status = new_subscription_status
            subscription.save()
            return Response({"message": "Subscription deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Subscriptions.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
