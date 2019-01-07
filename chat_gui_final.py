import wx
import chat_client
import threading

FRAME_SIZE = (1000, 600)

# CLIENT REQUEST IDENTIFIERS:
ENTRANCE_REQUEST_IDENTIFIER = 'ENTRANCE:'
BROADCAST_MESSAGE = 'BROADCAST:'
PRIVATE_MESSAGE = 'PRIVATE:'

# SERVER RESPONSE IDENTIFIERS
SUCCESSFUL_ENTRY = 'ENTERED SUCCESSFULLY'
WRONG_DETAILS = 'WRONG DETAILS'

CHAT_HISTORY = ''

USER_NOT_FOUND = '** Requested user does not exist, or is not connected **'


class PreEntrancePanel(wx.Panel):
    """ The first panel. in this panel, user will choose between
     registering to the system as a new user, and logging in. """

    def __init__(self, parent_frame):
        wx.Panel.__init__(self, parent=parent_frame, size=FRAME_SIZE)

        self.parent_frame = parent_frame  # parent frame.
        self.v_box = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.

        # Displaying a welcome text.
        self.welcome_text = wx.StaticText(self, label="welcome to Nadav's chat", style=wx.ALIGN_CENTRE)
        self.welcome_text.SetFont(
            wx.Font(30, wx.ROMAN, wx.NORMAL, wx.BOLD, False, u'Arial Rounded MT Bold'))  # setting font.

        # Creating the 'Login' & 'Register' buttons.
        self.login_button = wx.Button(self, label="login")
        self.register_button = wx.Button(self, label="register")

        # Binding buttons
        self.login_button.Bind(wx.EVT_BUTTON, self.update_entrance_login)
        self.register_button.Bind(wx.EVT_BUTTON, self.update_entrance_register)

        # Adding all of the objects in the panel to the sizer.
        self.v_box.AddSpacer(100)
        self.v_box.Add(self.welcome_text, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 40)
        self.v_box.Add(self.login_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.register_button, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Setting our sizer as the panel's sizer.
        self.SetSizer(self.v_box)

    def update_entrance_login(self, event):
        """ Updating the entrance type to 'login', and moving to the next panel. """
        self.parent_frame.set_entrance_type('login')
        self.parent_frame.switch_panels()

    def update_entrance_register(self, event):
        """ Updating the entrance type to 'register', and moving to the next panel. """
        self.parent_frame.set_entrance_type('register')
        self.parent_frame.switch_panels()


class UserEntrancePanel(wx.Panel):
    """ In this panel, user will be asked to enter username and password, which will be sent to the server. """

    def __init__(self, parent_frame):
        wx.Panel.__init__(self, parent=parent_frame, size=FRAME_SIZE)
        self.parent_frame = parent_frame  # parent frame
        self.v_box = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.
        self.username = ''  # username, initialized as ''
        self.password = ''  # password, initialized as ''
        self.password_validation_text = wx.StaticText(self, label='')  # print the password's validity.
        self.entrance_type = self.parent_frame.get_entrance_type()  # (entrance type: login\register)

        #  printing an instructions text to screen, according to entrance type
        if self.entrance_type == 'login':
            instructions_text = wx.StaticText(self, label="LOGIN \n \n enter username and password, then press 'done'.",
                                              style=wx.ALIGN_CENTRE)
        else:
            label = "REGISTRATION \n \n create your username and password, then press 'done'. \n" \
                    " *** password must be 6 characters long, and include at least one number ***"
            instructions_text = wx.StaticText(self, label=label, style=wx.ALIGN_CENTRE)

        instructions_text.SetFont(wx.Font(18, wx.ROMAN, wx.NORMAL, wx.NORMAL, False, u'Arial Rounded MT Bold'))  # font

        # username input
        username = wx.StaticText(self, label="Your username :", style=wx.ALIGN_CENTRE)
        edit_username = wx.TextCtrl(self)
        edit_username.Bind(wx.EVT_TEXT, self.update_username)

        # password input
        password = wx.StaticText(self, label="Your password :")
        edit_password = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        edit_password.Bind(wx.EVT_TEXT, self.update_password)

        # 'done' button. pressing this button will lead to sending
        #  the username and password to the server for verification
        done_button = wx.Button(self, label="done!")
        done_button.Bind(wx.EVT_BUTTON, self.wait_for_server_verification)

        # Adding all objects to the sizer.
        self.v_box.AddSpacer(100)
        self.v_box.Add(instructions_text, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.AddSpacer(30)
        self.v_box.Add(username, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.Add(edit_username, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.AddSpacer(20)
        self.v_box.Add(password, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.Add(edit_password, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.AddSpacer(20)
        self.v_box.Add(done_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.password_validation_text, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Setting our sizer as the panel's sizer.
        self.SetSizer(self.v_box)
        self.v_box.Layout()

    def update_username(self, event):
        """ updating username. """
        self.username = event.GetString()

    def update_password(self, event):
        """ updating password, and letting the user know whether or not the password they chose is strong enough. """
        self.password = event.GetString()
        if self.valid_password(self.password) and self.entrance_type is 'register':
            self.password_validation_text.SetLabel(' AMAZING password :) ')
            self.password_validation_text.SetForegroundColour(wx.Colour(0, 153, 0))  # setting color to GREEN
            self.v_box.Layout()
        elif self.valid_password(self.password) is False and self.entrance_type is 'register':
            self.password_validation_text.SetLabel(' BAD password :( ')
            self.password_validation_text.SetForegroundColour(wx.Colour(255, 0, 0))  # setting color to RED
            self.v_box.Layout()

    def valid_password(self, password):
        """ returns True if the password is at least 6 digits long and has at least one digit. Otherwise, False. """
        if len(password) > 5 and any(char.isdigit() for char in password):
            return True
        return False

    def wait_for_server_verification(self, event):
        """ sending connection details to the server for the server to verify. """
        if self.parent_frame.get_entrance_type() == 'login':
            self.parent_frame.client.client_socket.send(
                (ENTRANCE_REQUEST_IDENTIFIER + self.entrance_type + ':' + self.username + ':' + self.password).ljust(
                    1024, '0'))
            self.server_verification()

        elif self.parent_frame.get_entrance_type() == 'register':
            if self.valid_password(self.password):  # sending details to the server only if password is valid.
                self.parent_frame.client.client_socket.send(
                    (ENTRANCE_REQUEST_IDENTIFIER + self.entrance_type + ':' + self.username + ':' + self.password).ljust
                    (1024, '0'))
                self.server_verification()

    def server_verification(self):
        """ Receiving the server's response to the entrance attempt.
            if the attempt has succeeded, receiving the chat history. """
        global CHAT_HISTORY
        server_response = self.parent_frame.client.client_socket.recv(1024).split('0')[0]

        if server_response.startswith(SUCCESSFUL_ENTRY):  # if entry was successful:
            server_response = server_response.split('-')
            CHAT_HISTORY = server_response[1]  # Previous chatting history.

            self.parent_frame.set_username(self.username)  # updating username in the Frame class.
            self.parent_frame.switch_panels()  # switching panels.

        elif server_response == WRONG_DETAILS:  # if the entry failed:
            # presenting a message, accordingly.
            self.password_validation_text.SetLabel('WRONG USERNAME OR PASSWORD \n please try again.')
            self.v_box.Layout()


class ChatPanel(wx.Panel):
    """ In this panel, user will be able to send and receive broadcast or private messages from all of the other
        connected users."""

    def __init__(self, parent_frame):
        wx.Panel.__init__(self, parent=parent_frame, size=FRAME_SIZE)

        self.parent_frame = parent_frame  # parent frame.
        self.v_box = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.

        #  instructions text on how to send a private message.
        self.instructions = wx.StaticText(self, label="to send a private message to a specific user, \n enter user's "
                                                      "name, a '@' sign, and then the wanted message.",
                                          style=wx.ALIGN_CENTER)
        self.instructions.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Arial Rounded MT Bold'))

        # setting the textCtrl in which all messages will be shown.
        self.show_messages = wx.TextCtrl(self, value=CHAT_HISTORY, style=wx.TE_MULTILINE | wx.TE_READONLY,
                                         size=(800, 400))
        self.show_messages.SetFont(wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL, False, u'Arial Rounded MT Bold'))

        # setting the textCtrl to which the messages will be typed.
        self.enter_message = wx.TextCtrl(self, value='Your Text Here... (Press ENTER to send)', size=(800, 40),
                                         style=wx.TE_PROCESS_ENTER)
        self.enter_message.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Arial Rounded MT Bold'))

        self.enter_message.Bind(wx.EVT_TEXT_ENTER, self.send_message)  # binding textCtrl

        # Adding objects to sizer
        self.v_box.AddSpacer(10)
        self.v_box.Add(self.instructions, 0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND)
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.show_messages, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.enter_message, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Setting our sizer as the panel's sizer.
        self.SetSizer(self.v_box)
        self.v_box.Layout()

        # creating a thread with self.receive_messages as the target, so that messages will be received constantly.
        t = threading.Thread(target=self.receive_messages, args=())
        t.start()

    def send_message(self, event):
        """ responsible for sending private or broadcast messages. """
        message = event.GetString()

        if '@' in message:  # if message is intended to a specific user:
            self.parent_frame.client.client_socket.send(
                (PRIVATE_MESSAGE + self.parent_frame.get_username() + ':' + message).ljust(1024, '0'))

        else:  # if message is intended for all users:
            self.parent_frame.client.client_socket.send(
                (BROADCAST_MESSAGE + self.parent_frame.get_username() + ':' + message).ljust(1024, '0'))

        # resetting the input textCtrl value to be empty, once message is sent.
        self.enter_message.SetValue('')

    def receive_messages(self):
        """ responsible for receiving messages from the server. """
        while True:
            print threading.current_thread().getName()  # printing thread name, to track threading.
            message_received = self.parent_frame.client.client_socket.recv(1024).split('0')[0]  # receiving message.
            # if our private message was intended for a non existing or not connected user:
            if message_received == USER_NOT_FOUND:
                self.show_messages.AppendText(USER_NOT_FOUND + '\n')  # inform the user about it.

            else:
                message_received = message_received.split(':')
                if message_received[1] == self.parent_frame.get_username():  # if the message was sent by me:
                    self.show_messages.AppendText('You: ' + message_received[2] + '\n')
                else:  # if the message was sent by any of the other clients:
                    # append textCtrl text with the new message.
                    self.show_messages.AppendText(message_received[1] + ': ' + message_received[2] + '\n')


class Frame(wx.Frame):
    """ main frame. """

    def __init__(self, parent, title):
        super(Frame, self).__init__(parent, title=title, size=FRAME_SIZE,
                                    style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        self.SetIcon(wx.Icon("icon.ico"))  # setting icon.
        self.SetBackgroundColour((102, 205, 170))  # setting background color.

        self.client = chat_client.Client()  # creating client.
        self.client.send_key()  # sending encryption key to server

        self.entrance_type = ''  # initializing entrance type as ''
        self.username = ''  # initializing username as ''

        self.pre_entrance_panel = PreEntrancePanel(self)  # creating and showing the first panel.

        # initializing the next panels, afterwards they will become actual objects.
        self.user_entrance_panel = wx.Panel(self).Hide()
        self.chat_panel = wx.Panel(self).Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.
        self.sizer.Add(self.pre_entrance_panel, 1, wx.EXPAND)  # adding panel to sizer.
        self.SetSizer(self.sizer)  # Setting our sizer as the panel's sizer.

    def set_entrance_type(self, entrance_type):
        self.entrance_type = entrance_type

    def get_entrance_type(self):
        return self.entrance_type

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def switch_panels(self):
        """ responsible for switching panels. """
        if self.pre_entrance_panel.IsShownOnScreen():  # if first panel is shown:
            self.pre_entrance_panel.Hide()  # hide panel
            self.sizer.Remove(0)  # remove panel form the sizer
            self.user_entrance_panel = UserEntrancePanel(self)  # create the next panel
            self.sizer.Add(self.user_entrance_panel, 1, wx.EXPAND)  # add next panel to sizer.
            self.Layout()

        elif self.user_entrance_panel.IsShownOnScreen():
            self.SetTitle(self.username + "'s chat!")  # updating the frame's title according to the client's username.
            self.user_entrance_panel.Hide()  # hide panel
            self.sizer.Remove(0)  # remove panel form the sizer
            self.chat_panel = ChatPanel(self)  # create the next panel
            self.sizer.Add(self.chat_panel, 1, wx.EXPAND)
            self.Layout()  # add next panel to sizer.


def main():
    app = wx.App()
    frame = Frame(None, title="CHAT!")
    frame.Centre()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
