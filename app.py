from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# Initialize Flask-Mail
try:
    from flask_mail import Mail, Message
    mail = Mail(app)
    MAIL_ENABLED = True
except ImportError:
    MAIL_ENABLED = False
    print("Flask-Mail not installed. Email functionality will be disabled.")

@app.route('/')
def home():
    """Main portfolio page"""
    return render_template('home.html')

@app.route('/contact', methods=['POST'])
def contact():
    """Handle contact form submission - supports both regular and AJAX requests"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or 'application/json' in request.headers.get('Accept', '')
        
        if MAIL_ENABLED:
            try:
                # Create email message with improved headers
                msg = Message(
                    subject=f"New Portfolio Contact from {name}",
                    recipients=[os.environ.get('RECIPIENT_EMAIL', 'vanshgosavi7official@gmail.com')],
                    reply_to=email,
                    sender=os.environ.get('MAIL_USERNAME')
                )
                
                # Add custom headers to improve deliverability
                msg.extra_headers = {
                    'X-Priority': '1',
                    'X-MSMail-Priority': 'High',
                    'Importance': 'High',
                    'X-Mailer': 'Portfolio Contact Form'
                }
                
                # HTML email body for better formatting and deliverability
                msg.html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #f97316; color: white; padding: 20px; text-align: center; }}
                        .content {{ background-color: #f9f9f9; padding: 20px; }}
                        .field {{ margin-bottom: 15px; }}
                        .label {{ font-weight: bold; color: #f97316; }}
                        .message-box {{ background-color: white; padding: 15px; border-left: 4px solid #f97316; }}
                        .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>New Portfolio Contact Message</h2>
                        </div>
                        <div class="content">
                            <div class="field">
                                <span class="label">From:</span> {name}
                            </div>
                            <div class="field">
                                <span class="label">Email:</span> {email}
                            </div>
                            <div class="field">
                                <span class="label">Subject:</span> {subject}
                            </div>
                            <div class="field">
                                <span class="label">Message:</span>
                                <div class="message-box">
                                    {message.replace(chr(10), '<br>')}
                                </div>
                            </div>
                        </div>
                        <div class="footer">
                            <p>This message was sent from your portfolio contact form.</p>
                            <p>Reply directly to this email to respond to {name}.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Plain text version as fallback
                msg.body = f"""
NEW PORTFOLIO CONTACT MESSAGE

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This message was sent from your portfolio contact form.
Reply directly to this email to respond to {name}.
                """
                
                # Send email
                mail.send(msg)
                success_message = f'✅ Message sent successfully! Thank you {name}, I will respond within 24-48 hours.'
                
                if is_ajax:
                    return jsonify({
                        'status': 'success',
                        'message': success_message
                    })
                else:
                    flash(success_message, 'success')
                
            except Exception as e:
                print(f"Error sending email: {e}")
                warning_message = f'⚠️ Thank you {name}! Your message has been received, but there was an issue with email delivery. I will still get back to you soon.'
                
                if is_ajax:
                    return jsonify({
                        'status': 'warning',
                        'message': warning_message
                    })
                else:
                    flash(warning_message, 'warning')
        else:
            # Fallback when Flask-Mail is not available
            print(f"Contact form submission from {name} ({email}): {subject} - {message}")
            info_message = f'📝 Thank you {name}! Your message has been logged. Email service is currently offline, but I will get back to you soon.'
            
            if is_ajax:
                return jsonify({
                    'status': 'info',
                    'message': info_message
                })
            else:
                flash(info_message, 'info')
        
        # For non-AJAX requests, redirect as before
        if not is_ajax:
            return redirect(url_for('home') + '#contact')
        else:
            return jsonify({'status': 'success'})
    
    return redirect(url_for('home'))

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=8080)
else:
    # For Vercel deployment
    pass