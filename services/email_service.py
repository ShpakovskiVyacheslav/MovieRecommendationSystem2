import smtplib
from email.message import EmailMessage

def send_reset_code(email_to, code, email_address, app_password):
    """Отправка кода подтверждения на email пользователя"""
    try:
        msg = EmailMessage()
        msg['From'] = email_address
        msg['To'] = email_to
        msg['Subject'] = 'Код для сброса пароля'
        msg.set_content(f'Ваш код для сброса пароля: {code}\n\nКод действителен 10 минут.')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_address, app_password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False
