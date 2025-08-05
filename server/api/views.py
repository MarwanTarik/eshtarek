from tokenize import TokenError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .permissions import IsAdmin
from .serializers import *

# Create your views here.
class UserRegistrationView(APIView):    
    permission_classes = [AllowAny]

    def post(self, request):
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


class TenantRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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


class AdminRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        
        if serializer.is_valid():
            token_data = serializer.validated_data
            return Response(token_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PlanView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = PlanSerializer(data=request.data)
        if serializer.is_valid():
            plan = serializer.save(created_by=request.user)
            return Response(PlanSerializer(plan).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request, pk=None):
        if pk:
            try:
                plan = Plans.objects.get(pk=pk)
            except Plans.DoesNotExist:
                return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = PlanSerializer(plan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            plans = Plans.objects.all()
            serializer = PlanSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        try:
            plan = Plans.objects.get(pk=pk)
        except Plans.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            updated_plan = serializer.save()
            return Response(PlanSerializer(updated_plan).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        serializer = LimitPoliciesSerializer(data=request.data)
        if serializer.is_valid():
            limit_policy = serializer.save(created_by=request.user)
            return Response(LimitPoliciesSerializer(limit_policy).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            try:
                limit_policy = LimitPolicies.objects.get(pk=pk)
            except LimitPolicies.DoesNotExist:
                return Response({"error": "Limit policy not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = LimitPoliciesSerializer(limit_policy)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            limit_policies = LimitPolicies.objects.all()
            serializer = LimitPoliciesSerializer(limit_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

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