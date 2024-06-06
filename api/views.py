from api.serializer import PersonSerializer
from django.shortcuts import render
from rest_framework import generics, status, request
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import Person
from django.db.models import Q
import datetime
# Create your views here.

def validate_iin(iin):
    if len(iin) != 12 or not iin.isdigit():
        return False, "ИИН должен состоять из 12 цифр"


    weights1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    weights2 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]

    def calculate_checksum(iin, weights):
        sum = 0
        for i in range(11):
           sum += int(iin[i]) * weights[i]
        return sum % 11

    checksum1 = calculate_checksum(iin, weights1)
    if checksum1 == 10:
        checksum1 = calculate_checksum(iin, weights2)

    if checksum1 == 10 or checksum1 != int(iin[11]):
        return False, "Неверная контрольная цифра"

    return True, None
def get_birth_date_and_gender(iin):
    year = int(iin[0:2])
    month = int(iin[2:4])
    day = int(iin[4:6])
    code = int(iin[6])

    if code in [1, 2]:
        century = 1800
    elif code in [3, 4]:
        century = 1900
    elif code in [5, 6]:
        century = 2000
    else:
        return None, None, "Неверный код"

    year += century

    gender = "male" if code % 2 != 0 else "female"

    try:
        birth_date = datetime.datetime(year, month, day).strftime('%d.%m.%Y')
    except ValueError:
        return None, None, "Неверная дата рождения"

    return birth_date, gender, None

class PersonApiView(APIView):

    def post(self, request, format=None):

        birth_date, gender, birth_error = get_birth_date_and_gender(request.data['iin'])
        if birth_error:
            print(f"Ошибка определения даты рождения и пола: {birth_error}")

        is_valid, validation_error = validate_iin(request.data['iin'])

        resData = {
            "success": is_valid,
            "errors": validation_error
        }

        if not is_valid:
            print(f"Ошибка валидации ИИН: {validation_error}")
            return Response(resData,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        serializer = PersonSerializer(data=request.data)


        if serializer.is_valid() and is_valid:
            serializer.save()
            return Response(resData, status=status.HTTP_201_CREATED)

        return Response({"success": False,"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request, val,format=None):

        if 'iin_check' in request.path:
           return self.check_iin(request,val)
        elif 'people/info/iin' in request.path:
            return self.get_person_by_iin(request,val)
        elif 'people/info/fio' in request.path:
            return self.get_person_by_fio(request,val)
        else: return Response(status=status.HTTP_404_NOT_FOUND)


    def get_person_by_fio(self,request,fio):
        try:
            person = Person.objects.filter(
                Q(name__icontains=fio)
            )
            serializer = PersonSerializer(person, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Person.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_person_by_iin(self,request, iin):
        birth_date, gender, birth_error = get_birth_date_and_gender(iin)
        if birth_error:
            print(f"Ошибка определения даты рождения и пола: {birth_error}")
            # return

        is_valid, validation_error = validate_iin(iin)
        resData = {
            "success": is_valid,
            "errors": validation_error
        }

        if not is_valid:
            print(f"Ошибка валидации ИИН: {validation_error}")
            return Response(resData, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            person = Person.objects.get(iin=iin)

            serializer = PersonSerializer(person)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Person.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def check_iin(self, request,iin, format=None):

        birth_date, gender, birth_error = get_birth_date_and_gender(iin)

        is_valid, validation_error =  validate_iin(iin)

        resData = {'correct': is_valid, 'birth_date': birth_date, 'gender': gender, }

        if birth_error:
            print(f"Ошибка определения даты рождения и пола: {birth_error}")
            #return

        if not is_valid:
            print(f"Ошибка валидации ИИН: {validation_error}")
            return Response(resData,status=status.HTTP_400_BAD_REQUEST)


        return Response(resData, status=status.HTTP_200_OK)

