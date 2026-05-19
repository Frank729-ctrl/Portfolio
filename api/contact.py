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


def build_email(name: str, email: str, service: str, message: str) -> str:
    safe_name    = escape(name)
    safe_email   = escape(email)
    safe_service = escape(service)
    safe_message = escape(message).replace("\n", "<br />")

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width,initial-scale=1" /></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:48px 16px;">
  <tr><td align="center">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e4e4e7;">

      <!-- Header -->
      <tr>
        <td style="background:#0a0a0a;padding:28px 32px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <p style="margin:0 0 6px;font-family:'Courier New',Courier,monospace;font-size:11px;text-transform:uppercase;letter-spacing:0.12em;color:#71717a;">Portfolio &mdash; Contact Form</p>
                <p style="margin:0;font-size:20px;font-weight:600;color:#ededed;letter-spacing:-0.02em;">New enquiry from {safe_name}</p>
              </td>
              <td align="right" valign="top" style="padding-left:16px;white-space:nowrap;">
                <span style="display:inline-block;background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.3);border-radius:999px;padding:4px 12px;font-family:'Courier New',Courier,monospace;font-size:11px;color:#4ade80;">&bull; New</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- Service badge -->
      <tr>
        <td style="padding:24px 32px 0;">
          <span style="display:inline-block;background:#f4f4f5;border:1px solid #e4e4e7;border-radius:6px;padding:5px 12px;font-family:'Courier New',Courier,monospace;font-size:12px;color:#52525b;">Service &rarr; {safe_service}</span>
        </td>
      </tr>

      <!-- Message -->
      <tr>
        <td style="padding:20px 32px 24px;">
          <p style="margin:0 0 8px;font-size:11px;font-family:'Courier New',Courier,monospace;text-transform:uppercase;letter-spacing:0.1em;color:#71717a;">Message</p>
          <div style="background:#fafafa;border:1px solid #e4e4e7;border-left:3px solid #0a0a0a;border-radius:6px;padding:16px 18px;font-size:15px;line-height:1.7;color:#18181b;">{safe_message}</div>
        </td>
      </tr>

      <!-- Contact details -->
      <tr>
        <td style="padding:0 32px 28px;">
          <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e4e4e7;border-radius:8px;overflow:hidden;">
            <tr style="background:#fafafa;">
              <td style="padding:12px 16px;border-bottom:1px solid #e4e4e7;width:50%;">
                <p style="margin:0 0 3px;font-size:10px;font-family:'Courier New',Courier,monospace;text-transform:uppercase;letter-spacing:0.1em;color:#71717a;">Name</p>
                <p style="margin:0;font-size:14px;color:#18181b;font-weight:500;">{safe_name}</p>
              </td>
              <td style="padding:12px 16px;border-bottom:1px solid #e4e4e7;border-left:1px solid #e4e4e7;width:50%;">
                <p style="margin:0 0 3px;font-size:10px;font-family:'Courier New',Courier,monospace;text-transform:uppercase;letter-spacing:0.1em;color:#71717a;">Service</p>
                <p style="margin:0;font-size:14px;color:#18181b;font-weight:500;">{safe_service}</p>
              </td>
            </tr>
            <tr style="background:#ffffff;">
              <td colspan="2" style="padding:12px 16px;">
                <p style="margin:0 0 3px;font-size:10px;font-family:'Courier New',Courier,monospace;text-transform:uppercase;letter-spacing:0.1em;color:#71717a;">Email</p>
                <p style="margin:0;font-size:14px;color:#18181b;font-weight:500;">{safe_email}</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- Reply CTA -->
      <tr>
        <td style="padding:0 32px 32px;">
          <a href="mailto:{safe_email}" style="display:inline-block;background:#18181b;color:#ffffff;text-decoration:none;padding:11px 24px;border-radius:999px;font-size:14px;font-weight:500;letter-spacing:-0.01em;">Reply to {safe_name} &rarr;</a>
        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="background:#fafafa;border-top:1px solid #e4e4e7;padding:16px 32px;">
          <p style="margin:0;font-size:11px;color:#a1a1aa;font-family:'Courier New',Courier,monospace;">Sent via portfolio contact form &mdash; Frank Dela Nutsukpuie</p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


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
            "reply_to": str(form.email),
            "subject": f"[Portfolio] {form.service} — {form.name}",
            "html": build_email(
                name=form.name.strip(),
                email=str(form.email),
                service=form.service,
                message=form.message.strip(),
            ),
        })
    except Exception as e:
        raise HTTPException(500, str(e))

    return {"ok": True}
