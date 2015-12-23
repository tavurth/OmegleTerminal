#! /usr/bin/python

################################################################################################################
################################################################################################################
##
## 		
## 		Copyright 2015 William Whitty
## 		will.whitty.arbeit@gmail.com
## 		
## 		Licensed under the Apache License, Version 2.0 (the "License");
## 		you may not use this file except in compliance with the License.
## 		You may obtain a copy of the License at
## 		
## 		    http://www.apache.org/licenses/LICENSE-2.0
## 		
## 		Unless required by applicable law or agreed to in writing, software
## 		distributed under the License is distributed on an "AS IS" BASIS,
## 		WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## 		See the License for the specific language governing permissions and
## 		limitations under the License.
## 		
##				
################################################################################################################
################################################################################################################

# Import STD
import sys
import json
import time
import threading
import urllib2 as web

# Import Global
# Import Local

def help_function():
    print """
            ___           ___           ___           ___           ___       ___     
           /\  \         /\__\         /\  \         /\  \         /\__\     /\  \    
          /::\  \       /::|  |       /::\  \       /::\  \       /:/  /    /::\  \   
         /:/\:\  \     /:|:|  |      /:/\:\  \     /:/\:\  \     /:/  /    /:/\:\  \  
        /:/  \:\  \   /:/|:|__|__   /::\~\:\  \   /:/  \:\  \   /:/  /    /::\~\:\  \ 
       /:/__/ \:\__\ /:/ |::::\__\ /:/\:\ \:\__\ /:/__/_\:\__\ /:/__/    /:/\:\ \:\__\ 
       \:\  \ /:/  / \/__/~~/:/  / \:\~\:\ \/__/ \:\  /\ \/__/ \:\  \    \:\~\:\ \/__/
        \:\  /:/  /        /:/  /   \:\ \:\__\    \:\ \:\__\    \:\  \    \:\ \:\__\  
         \:\/:/  /        /:/  /     \:\ \/__/     \:\/:/  /     \:\  \    \:\ \/__/  
          \::/  /        /:/  /       \:\__\        \::/  /       \:\__\    \:\__\    
           \/__/         \/__/         \/__/         \/__/         \/__/     \/__/    

        Coded by William Whitty.
        Connects you to Omegle.com, a site for talking with random strangers.

        Type:

           next > End the conversation and move to the next stranger
           kill > End all conversations and quit the program
           help > Show this dialog
    """

class Omegle:
    """ Used for communication with Omegle """
    
    def __init__(self, **kwargs):
        """ Our constructor """

        # Our connection ID
        self.handle   = None
        self.stranger = None
        
        # Begin a connection
        if kwargs.get('connect', True):
            self.connect()

    def error(self, message = ''):
        """ Give an error to the stdout """
        print "Error: " + message

    def valid(self):
        """ Check the validity of internal variables """

        # We were unable to create a connection
        if self.handle == '{}':
            self.error('could not connect to Omegle.com')
            return False

        # Everything is correct
        return True
    
    def response(self):
        """ Get a RAW response from the stranger """
        try:
            return web.urlopen(self.stranger).read()
        except:
            return ''

    def wait_callback(self):
        """ Called when we are waiting for a connection """
        print 'Waiting...'

    def conn_callback(self):
        """ Called when we are connected to an active user """
        print 'Connected to a random stranger!\n'

    def exit_callback(self):
        """ Called when we are disconnected from a session """
        print 'Stranger disconnected!\n'
        self.connect()

    def type_callback(self):
        """ Called when the stranger is typing """
        print 'Stranger is typing...'

    def hear_callback(self, message):
        """ Called when the stranger sends us a message """
        print 'Stranger: ' + message

    def listen(self):
        """ Used to listen for convesation partner input """

        # Error checking
        if not self.valid():
            return
        
        # Loop until told to quit
        while True:

            # Get a response from the stranger
            response = self.response()

            # If the stranger has disconnected
            if 'strangerDisconnected' in response:
                self.exit_callback()

            # If the stranger is typing...
            elif 'typing' in response:
                self.type_callback()

            # If the stranger has sent us a message
            elif 'gotMessage' in response:
                self.hear_callback(response[16 : -3])

    def connect(self):
        """ Begin a new conversation """
        # Initialise the connection and return the url
        self.handle = web.urlopen('http://omegle.com/start').read()

        # Check for errors
        if not self.valid():
            return

        # Strip the handle string of quotations
        self.handle = self.handle[1 : -1]

        # Save our nevent request
        self.stranger = web.Request('http://omegle.com/events', 'id=' + self.handle)

        # Get the response
        response = self.response()
        
        # If we're still waiting for a stranger
        if 'waiting' in response:
            self.wait_callback()

        # If we've got a good connection
        if 'connected' in response:
            self.conn_callback()

    def process(self, message):
        """ Check user input for terminal commands """
        # Check for our exit button
        if message == 'kill':
            quit(0)

        # Check for a help request
        if message == 'help':
            help_function()
            return True

        # No processing
        return False
            
    def type(self):
        """ Tell Omegle that we're typing something """

        # Check for a valid handle
        if not self.valid():
            return

        # Tell Omegl that we're typing
        web.urlopen('http://omegle.com/typing', 'id=' + self.handle).close()
    
    def talk(self, message, **kwargs):
        """ Send a message to our conversation partner """
        
        # Output to the terminal
        if kwargs.get('show', True):
            print 'You: ' + message

        # Process terminal commands
        if kwargs.get('process', True):
            if self.process(message):
                return

        # Error checking
        if not self.valid():
            return
            
        # Talk to Omegle
        msgReq = web.urlopen('http://omegle.com/send', 'msg=' + message + '&id=' + self.handle).close()

    def start_thread(self):
        """ Begins a listener in a seperate thread, so that the user can give input """
        # Set our listener function as the thread callback
        self.listener = threading.Thread(target=self.listen)

        # Specify that this thread should not prevent us from exiting the program
        self.listener.daemon = True

        # Start the thread
        self.listener.start()
        
    def user_input(self):
        """ Called when the stranger sends us a message """

        # Pointer to internal thread
        self.listener = None
        
        while True:
            # Connect to a new stranger
            self.connect()
            
            # Start listening
            self.start_thread()

            while True:

                # Tell Omegle that we're typing
                self.type()

                # Get some input from the user
                input = raw_input()

                if 'next' in input:
                    self.listener.join(0)
                    break

                # Send the text to the stranger
                self.talk(input, show=False)

if __name__ == '__main__':

    # Display the user help
    help_function()
    
    # Create our Omegle instance
    handle = Omegle(connect=False)
    handle.user_input()
