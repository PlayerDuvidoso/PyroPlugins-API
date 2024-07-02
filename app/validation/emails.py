from decouple import config
import yagmail




class Emails():

    email = config("EMAIL")
    password = config("EMAIL_PASSWORD")

    def send_email(self, subject, to_email, message):

        yagmail.SMTP({self.email: "PyroPlugins"}, self.password).send(to_email, subject, message)

    def send_verification(self, to_email, code):
        
        subject = "Código de verificação"

        contents = [
            "Ative agora sua conta clicando no link abaixo: ",
            f'<a href="https://webhook.duvidoso.uk/verify_user/{code}">Ativar Conta</a>'
        ]

        yagmail.SMTP({self.email: "PyroPlugins"}, self.password).send(to_email, subject, contents=contents)