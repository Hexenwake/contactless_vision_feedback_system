import pyrebase


class RealtimeFirebaseGet:
    def __init__(self):
        config = {
            "apiKey": "AIzaSyDlKTygb8q0xeeF1imfy-5t7aROHlnO3Jk",
            "authDomain": "dp3-ifs-system.firebaseapp.com",
            "databaseURL": "https://dp3-ifs-system-default-rtdb.asia-southeast1.firebasedatabase.app",
            "projectId": "dp3-ifs-system",
            "storageBucket": "dp3-ifs-system.appspot.com",
            "messagingSenderId": "195243684514",
            "appId": "1:195243684514:web:1f00bc947f1f2789825dfb",
            "measurementId": "G-EJFR17XK68"
        }

        firebase = pyrebase.initialize_app(config)
        self.data = firebase.database().child("Questions").get()
        # print(data.each())
        self.size = len(self.data.each())
        self.width = 3

        self.height = int(self.size / self.width)
        if self.size % self.width != 0:
            self.height += 1

    def get_data(self):
        page_data = [[0 for x in range(self.width)] for y in range(self.height)]
        i, j = 0, 0
        for question in self.data.each():
            question_dict = question.val()
            # print(question_dict["questionName"])
            page_data[j][i] = question_dict["questionName"]
            if i < 2:
                i += 1
            else:
                i = 0
                j += 1
        return page_data

    def reset(self):
        self.__init__()


class RealtimeFirebaseUpload:
    def __init__(self):
        config = {
            "apiKey": "AIzaSyDlKTygb8q0xeeF1imfy-5t7aROHlnO3Jk",
            "authDomain": "dp3-ifs-system.firebaseapp.com",
            "databaseURL": "https://dp3-ifs-system-default-rtdb.asia-southeast1.firebasedatabase.app",
            "projectId": "dp3-ifs-system",
            "storageBucket": "dp3-ifs-system.appspot.com",
            "messagingSenderId": "195243684514",
            "appId": "1:195243684514:web:1f00bc947f11f2789825dfb",
            "measurementId": "G-EJFR17XK68"
        }

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def upload(self, answer):
        parent_path = self.check_test()
        self.db.child("reviews").child(parent_path).set(answer)

    def check_test(self):
        location_ref = self.db.child("reviews")
        keys = location_ref.shallow().get()
        if keys.val() is None:
            print('no reviews')
            return 1
        # Convert the keys dictionary into a list
        parent_keys = list(keys.val())
        int_parent_keys = [int(i) for i in parent_keys]

        if len(int_parent_keys) != 0:
            highest_value = max(int_parent_keys)
            res = highest_value + 1

        return res


print(RealtimeFirebaseUpload().check_test())
