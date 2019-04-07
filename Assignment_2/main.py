from google.appengine.ext import ndb
import webapp2
import renderer
import utilities
from anagram import Anagram
from addWord import AddWord

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        if utilities.user_is_logged_in():

            if not utilities.user_exists():
                utilities.add_new_user(utilities.get_user())
            result, wordCount, totalCount = utilities.get_anagrams_of_user(utilities.get_my_user())
            renderer.render_main(self, utilities.get_logout_url(self), result, wordCount, totalCount)

        else:
            renderer.render_login(self, utilities.get_login_url(self))


    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        my_user = utilities.get_my_user()
        button = self.request.get('button')
        input_text = utilities.prepare_text_input(self.request.get('value'))
        file = self.request.get('uploadFile')

        if button == 'Upload':
            openFile = open(file)
            readLine = openFile.readline()
            while readLine:
                word = (readLine.strip('\n\r')).lower()

                permutations = utilities.all_permutations(word)
                wordsinfo = utilities.filter_english_words(permutations)

                anagram_id = my_user.key.id() + '/' + utilities.generate_id(word)
                anagram_key = ndb.Key(Anagram, anagram_id)
                anagrams = anagram_key.get()

                if anagrams:

                    utilities.add_to_anagram(word, wordsinfo, anagram_key)
                else:

                    utilities.add_new_anagram(my_user, word, wordsinfo, anagram_id, anagram_key)

                readLine = openFile.readline()

            openFile.close()
            self.redirect('/')
        if button == 'Search':
            search_result = self.search(input_text, my_user)
            renderer.render_search(self, input_text, search_result)
        elif button == 'Generate':
            words = self.generate(input_text, my_user)
            renderer.render_search(self, input_text, words)

    def search(self, text, my_user):
        anagram_id = my_user.key.id() + '/' + utilities.generate_id(text)
        anagram = ndb.Key(Anagram, anagram_id).get()

        if anagram:
            result = anagram.words
            result.remove(text)
            return result
        else:
            return None

    def generate(self, input_text, my_user):
        permutations = utilities.all_permutations(input_text)
        anagrams = Anagram.query().fetch()
        sorted_list= []
        result = []
        for i in range(len(anagrams)):
            sorted_list.append(anagrams[i].sorted_word)
        for i in permutations:
            for j in sorted_list:
                if i == j:
                    anagram_id = my_user.key.id() + '/' + j
                    anagram = ndb.Key(Anagram, anagram_id).get()
                    for x in anagram.words:
                        result.append(str(x))
        if input_text in result:
            result.remove(input_text)
        return result

app = webapp2.WSGIApplication(
    [
        ('/', MainPage),
        ('/addWord', AddWord)
    ], debug=True)
