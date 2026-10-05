from .models import  Assignment, Enrollment, Lesson, Profile, Results, Submission, Teacher, Student,Course
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notice


from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model() # Project-e je User model configured ache, seta dao


class RegisterSerializer(serializers.ModelSerializer):
    hone = serializers.CharField(required=True, write_only=True)#write_only=True-->Field-e data pathano jabe, kintu response-e oi data dekhabe na.
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    # Only an admin can reach this endpoint, so letting the caller pick the
    # role is safe. Left out, the account is a student.
    role = serializers.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        required=False,
        default=Profile.STUDENT,
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'phone', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']#id client/frontend nijer moto set korte parbe na. Database automatically id generate korbe.
        extra_kwargs = {'password': {'write_only': True}}#password input hisebe nite parbe, but serializer response-e password dekhabe na.

    def validate_phone(self, value):
        if Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("That username is already taken.")
        return value

    def validate_password(self, value):
        # Run Django's own password rules, the same ones the reset flow uses.
        validate_password(value)
        return value


    @transaction.atomic #create ei function-er moddhe database-er shob operation successful hole commit, kono ekta fail hole shob rollback.
    def create(self, validated_data):
        phone = validated_data.pop('phone')#validated_data theke "phone" ber kore phone variable-e rakha hocche
        email = validated_data.pop('email')
        role = validated_data.pop('role', Profile.STUDENT)
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
        )
        Profile.objects.create(user=user, phone=phone, role=role)
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['role'] = instance.profile.role
        return data
# ModelSerializer normally User-er data return kore, 
# super().to_representation(instance) diye shei normal data-ta neya hocche. 
# Then instance.profile.role diye oi User-er Profile theke role ber kore data-r moddhe add kora hocche.
# Sheshe return data diye frontend-ke final data deya hocche।






class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)





class ProfileUpdateSerializer(serializers.Serializer):
    """“User nijer profile-e shudhu je information gula change korar permission ache, 
        sheigulai change korte parbe.”
    
    Not on this list, on purpose:
      Role → nijer role nijey change korte parbe na; admin change korbe.

      Username → change korte parbe na.

      Password → ekhane change hobe na; password-er jonno alada endpoint ache, 
                 karon age current password verify korte hobe.
    """

    #jaja change kora jabe tata rakha hoyeche 
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, max_length=20)

    def validate_phone(self, value):#DRF-er ekta convention ache je kono specific field-er custom validation korte hole function-er naam validate_<field_name> dite hoy
        if not value:
            raise serializers.ValidationError(
                "Your phone number is how you sign in, so it cannot be blank."
            )
#Ei part-ta basically check korche user je phone number-ta update korte chacche, seta onno kono user already use korche kina।
        me = self.context["request"].user #currently login kora user-ke me variable-e rakha hocche।
        if Profile.objects.filter(phone=value).exclude(user=me).exists():#.exclude(user=me) diye current user-ke bad diye onnoder profile check korche
            raise serializers.ValidationError(
                "Another account already uses that phone number."
            )
        return value

    def validate_email(self, value):
        # Password reset looks an account up by email, so two accounts sharing
        # one would make that ambiguous.
        me = self.context["request"].user
        if User.objects.filter(email__iexact=value).exclude(pk=me.pk).exists():
            raise serializers.ValidationError(
                "Another account already uses that email address."
            )
        return value

    @transaction.atomic
    def save(self, **kwargs):
        me = self.context["request"].user #me = currently login kora user.
        data = self.validated_data #data = is_valid() er por validation pass kora data.

        for field in ("first_name", "last_name", "email"):
            if field in data:
                setattr(me, field, data[field])#setattr() Python-er built-in function, jar kaj holo object-er kono attribute-er value set/update kora
        me.save()

        if "phone" in data: #Request-e phone deya hoyeche kina check kore.
            profile = Profile.objects.filter(user=me).first()#Current user-er Profile ber kore.
            if profile:
                profile.phone = data["phone"]#Profile-er ager phone number-er jaygay notun phone number bosay
                profile.save()

        return me






class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
#ekhane ekhono validation hoy nai।,,,Ei line-gula shudhu bole dicche frontend/user theke kon kon data serializer accept korbe।
#Ei fields-gula user/frontend theke kon data neya hobe seta define kore. 
#is_valid() call korar por data validate hoy, ebong valid data validated_data-te paoa jay.
    

#frontend theke asha current password-ta actually correct kina check kora।'    
    def validate_current_password(self, value):#Ekhane value holo frontend theke pathano current_password।
        if not self.context["request"].user.check_password(value):#currently login kora user.
            raise serializers.ValidationError("That is not your current password.")
        return value
#.check_password(value)-> oi logged-in user-er database-e thaka password-er sathe frontend theke asha current password-ta compare kore.

#Uddessho: user new_password ar confirm_password same diyeche kina check kora।    
    def validate(self, attrs):#attrs er moddhe frontend theke asha 3 ta password-er data thake:current/new/confirm_password,,
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "The two new passwords do not match."
            })
        if attrs["new_password"] == attrs["current_password"]:
            raise serializers.ValidationError({
                "new_password": "The new password has to be different from the old one."
            })
        #new password-ta project-er password requirements follow korche kina check hobe।
        validate_password(attrs["new_password"], user=self.context["request"].user)
        return attrs

#password 
# validate_current_password → fixed na, validate_<field_name> convention
# validate → DRF-er built-in serializer validation method
# validate_password → Django-r built-in password validation function
#API/data niye kaj korle DRF, Django-r core/backend kaj hole Django.





# uddessho holo password reset request-er jonno frontend theke user-er email neya।
# Frontend jokhon password reset korte chaibe, tokhon backend-e email pathabe,
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
#Important: ei serializer nije password reset kore na। 
# Eta shudhu password reset request-er jonno email input receive + validate korar kaj kore।
#Frontend shudhu email pathay...Backend-er uddesshe...Ei email-er account-er jonno password reset 
#process start koro....Tarpor normally backend email-e password reset link/token pathay।



#ChangePasswordSerializer-->Eta use hoy jokhon user already login kora ache ebong nijer password change korte chacche।
#PasswordResetRequestSerializer--> Eta use hoy jokhon user password bhule geche ebong login korte parche na।





#uddessho:  PasswordResetConfirmSerializer-er uddessho holo,user password vule jawar por 
# reset link theke paoa uid ar token verify kora. user je notun password dicche seta valid kina check kora।
#So, eta ensure kore je reset link valid, token valid, correct user identify kora jacche, 
# ar new password password rules follow korche
class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=uid, is_active=True)
        except Exception:
            raise serializers.ValidationError({
                "uid": "Invalid reset link."
            })

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({
                "token": "Invalid or expired reset token."
            })

        validate_password(attrs["new_password"], user=user)

        attrs["user"] = user
        return attrs




# The rows below carry the id of whatever they point at — a course sends
# {"teacher": 3} — and the table wants to show a name. Each serializer that
# has a foreign key therefore also sends the name behind it, read-only.
#
# The alternative was for the browser to download every teacher, every course
# and every student and do the join itself. That worked while the lists came
# back whole, but a page of ten rows should not cost eight thousand, and a
# lookup list that is itself paginated cannot answer for a row on page 40.
# The joins are already in the queryset via select_related, so the names cost
# nothing extra to send.

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'email', 'subject', 'is_active']
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'enrollment_date', 'is_active', 'roll_number']

class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'teacher_name']

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'enrollment_date',
            'student_name', 'course_title',
        ]

class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'course', 'course_title']
class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'lesson', 'due_date', 'course',
            'course_title', 'lesson_title',
        ]
class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    assignment_title = serializers.CharField(
        source='assignment.title', read_only=True,
    )

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'student', 'submitted_at', 'content',
            'student_name', 'assignment_title',
        ]
class ResultSerializer(serializers.ModelSerializer):
    # Two relations deep: a result points at a submission, which points at the
    # student and the assignment. "Submission #4" on its own says nothing.
    student_name = serializers.CharField(
        source='submission.student.name', read_only=True,
    )
    assignment_title = serializers.CharField(
        source='submission.assignment.title', read_only=True,
    )

    class Meta:
        model = Results
        fields = [
            'id', 'submission', 'score', 'feedback',
            'student_name', 'assignment_title',
        ]




class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = "__all__"