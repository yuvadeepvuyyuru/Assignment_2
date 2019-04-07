from google.appengine.ext import ndb
import webapp2
import renderer
import utilities
import os
import jinja2
from anagram import Anagram

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class AddWord(webapp2.RequestHandler):
    # GET-request
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_values = {
                'user': utilities.get_user(),
                'anagrams': utilities.get_anagrams_of_user(utilities.get_my_user())
                }
        template = JINJA_ENVIRONMENT.get_template('AddWord.html')
        self.response.write(template.render(template_values))

    # POST-request
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        if self.request.get('cancel') == 'Cancel':
            return self.redirect("/")
        # Get user data object from datastore of current user (logged in)
        my_user = utilities.get_my_user()
        input_text = utilities.prepare_text_input(self.request.get('value'))
        self.add(input_text, my_user)

    def add(self, text, my_user):
        permutations = utilities.all_permutations(text)
        words = utilities.filter_english_words(permutations)
        if text is not None or text != '':
            # Add anagram to datastore
            anagram_id = my_user.key.id() + '/' + utilities.generate_id(text)
            anagram_key = ndb.Key(Anagram, anagram_id)
            anagrams = anagram_key.get()

            if anagrams:
                # Anagram with this key already exists
                utilities.add_to_anagram(text, words, anagram_key)
            else:
                # This key doesnt exist so creates a new anagram object to datastore
                utilities.add_new_anagram(my_user, text, words, anagram_id, anagram_key)
        self.redirect("/")
