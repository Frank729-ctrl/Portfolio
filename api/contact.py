from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import resend
import os
from html import escape

app = FastAPI()


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    service: str = "General Enquiry"
    message: str


@app.post("/api/contact")
async def contact(form: ContactForm):
    if len(form.name.strip()) < 2:
        raise HTTPException(400, "Name too short")
    if len(form.message.strip()) < 10:
        raise HTTPException(400, "Message too short")

    resend.api_key = os.environ["RESEND_API_KEY"]
    to_email = os.environ.get("TO_EMAIL", "fradela39@gmail.com")

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": to_email,
            "reply_to": form.email,
            "subject": f"[Portfolio] {form.service} — {form.name}",
            "html": f"""
                <p><strong>Name:</strong> {escape(form.name)}</p>
                <p><strong>Email:</strong> {escape(str(form.email))}</p>
                <p><strong>Service:</strong> {escape(form.service)}</p>
                <hr />
                <p>{escape(form.message).replace(chr(10), '<br />')}</p>
            """,
        })
    except Exception as e:
        raise HTTPException(500, str(e))

    return {"ok": True}
