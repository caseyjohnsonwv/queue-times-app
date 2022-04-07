import time
import uuid
from fastapi import APIRouter, Form, Response
from utils.aws import DynamoDB
from utils.sms import reply_to_sms
import utils.nlp as nlp


router = APIRouter(prefix='/alerts')


@router.post('/twilio')
async def sms_reply(From: str = Form(...), Body: str = Form(...)):
    msg = Body
    phone_number = From

    alert_id = str(uuid.uuid4())
    park = nlp.extract_park(msg)
    ride = nlp.extract_ride(msg, park.park_id)
    wait_time = nlp.extract_wait_time(msg)
    start_time = time.time()
    end_time = start_time + 7200 #default of 2 hours

    alert = DynamoDB.AlertRecord(
        alert_id,
        phone_number,
        park.park_id,
        ride.ride_id,
        wait_time,
        start_time,
        end_time,
    )
    alert.write_to_dynamo()

    reply = f"Alert created! I'll watch for a wait under {wait_time} minutes on {ride.ride_name}. Powered by https://queue-times.com/"
    response = reply_to_sms([reply])
    return Response(content=str(response), media_type="application/xml")