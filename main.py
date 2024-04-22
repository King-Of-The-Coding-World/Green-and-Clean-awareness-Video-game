from sys import argv, exit

from PySide6 import QtCore
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtTextToSpeech import QTextToSpeech
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QLabel, QPushButton, QMainWindow, QGraphicsOpacityEffect, QApplication
from screeninfo import get_monitors


# CREATING A TRANSPARENT MASK CLASS TO MOVE THE GAME WINDOW
class transparent_mask(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.oldPosition = None
        self.setMouseTracking(True)

    def mousePressEvent(self, ev):
        self.oldPosition = ev.position()

    def mouseMoveEvent(self, ev):
        if ev.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.window().move(
                ev.globalPosition().x() - self.oldPosition.x(), ev.globalPosition().y() - self.oldPosition.y())


class Game(QMainWindow):
    def __init__(self):
        super().__init__()
        ###################################################################################
        # REQUIRED VARIABLES AND WIDGETS.

        self.monitor = get_monitors()[0]
        self.leaf_x, self.leaf_y = 10, 2
        self.leaf_file = "assets/basil-left.png"
        self.num = 0
        self.should_speak = True
        self.intro_string = '''
Dear friend, Welcome to the Green and Clean Video Game! This game is
designed to help you learn about different measures you can take to
make the environment cleaner and greener, all while having fun!
You will first play a game and after that you will have a small quiz
to make you know about some interesting facts and information. So, why
wait? Click the 'Get Started' button below and let's dive into the game!
'''
        self.stage1_msgs = ["Before telling you the measures that keep the environment clean",
                            "It's important to make you understand the importance of cleanliness",
                            "In front of your eyes there is a dirty, ugly park.",
                            "Your task is to remove all the garbage and dirt from the park",
                            "It's simple. To remove an item, simply click on it and it will vanish",
                            "And here you go!!!!"]
        self.stage1_msgs_index = 0
        self.current_stage_msg = self.stage1_msgs[self.stage1_msgs_index]
        self.stage_item_count = 0

        self.info_stage_string = '''
Well done! You have just made a park happier and healthier. You can compare
the images of the park when it was filled with garbage to the one when you
cleaned it. This tells you how important the cleanliness is! If you learn it
without yawning a single time, the game has achieved its goal. After
this game, you are going to have a small quiz so that you can gain some
knowledge that will be helpful for you. Just press the 'Start Quiz' button below.
'''
        self.quiz_score = 0
        self.ques_list = ['What is the largest rainforest in the world?',
                          'What is the largest coral reef system in the world?',
                          'How much solid waste does the world generate in just one day?',
                          'What is the name of the largest desert in the world?',
                          'What is the name of the largest river in the world?',
                          'What is the name of the largest mountain range in the world?',
                          'What is the name of the largest lake in the world?',
                          'When World Cleanup Day is celebrated in the year?',
                          'When was the Clean India Mission launched?',
                          'Name the gas that is one of the main cause of global warming?', None]

        '''Correct Answers: 1. Amazon Rainforest, 2. Great Barrier Reef, 3. 3.5 million tons, 4. Sahara Desert
        5. Amazon River, 6. The Andes, 7. Caspian Sea, 8.third saturday of september, 9. 2 October 2014, 10. All of these'''

        self.op1_list = ["Amazon Rainforest", "Grant Barrier Reef", "4.7 million tons", "Thar Desert", "Ganga River",
                         "Rocky Mountains", "Caspian Sea", "3rd saturday of september", "5th september 2012",
                         "Carbon Dioxide", None]
        self.op2_list = ["Sundarban Rainforest", "Grant Nile Reef", "3.6 million tons", "Sahara Desert", "Amazon River",
                         "The Great Himalayas", "Black Sea", "1st of November", "14th november 2014", "Methane", None]
        self.op3_list = ["African Rainforest", "Great Barrier Reef", "3.5 million tons", "Antarctic Ice Sheet",
                         "Nile River", "The Andes", "Superior", "December 23", "2nd October 2014", "Nitrous Oxide",
                         None]
        self.op4_list = ["None of these", "Lakshadweep Reef", "5 million tons", "Gobi Desert", "Brahmaputra River",
                         "The Great Heights", "Victoria", "22nd January", "3rd August 2014", "All of these", None]
        self.correct_answers = [self.op1_list, self.op3_list, self.op3_list, self.op2_list, self.op2_list,
                                self.op3_list, self.op1_list, self.op1_list, self.op3_list, self.op4_list, None]

        self.knowledge = '''
Here are a few easy and effective ways you can choose to reduce your
daily impact and make the earth clean and green!

1. Say no to single-use plastic.
2. Promote reusable products.
3. Throw the waste in dustbin only.
4. Use Compost to grow crops and reduce the use of chemicals.
5. Remember the 5 R's.
6. Say no to bad habits like smoking, drug-use, etc.
7. Eat healthy food.
8. Grow more and more plants.
9. Influence others to do the same.
'''

        self.index_no = 0

        # These are our speakers and players that we will use to speak and play audio anytime we want in the program.
        self.speaker = QTextToSpeech(self)
        try:
            self.speaker.setVoice(self.speaker.availableVoices()[2])
        except IndexError:
            self.speaker.setVoice(self.speaker.availableVoices()[1])

        # stage one background sound
        self.stage1_bg_audio_output = QAudioOutput(self)
        self.stage1_bg_player = QMediaPlayer(self)
        self.stage1_bg_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.stage1_bg_player.setAudioOutput(self.stage1_bg_audio_output)
        self.stage1_bg_player.setSource(QtCore.QUrl.fromLocalFile("assets/bg-song stage1.mp3"))

        # stage 1 victory sound
        self.stage1_victory_audio_output = QAudioOutput(self)
        self.stage1_victory_sound = QMediaPlayer(self)
        self.stage1_victory_sound.setAudioOutput(self.stage1_victory_audio_output)
        self.stage1_victory_sound.setSource(QtCore.QUrl.fromLocalFile("assets/stage 1 clear.mp3"))

        # stage 1 item clicked sound
        self.stage1_item_click_sound_output = QAudioOutput(self)
        self.stage1_item_click_sound = QMediaPlayer(self)
        self.stage1_item_click_sound.setAudioOutput(self.stage1_item_click_sound_output)
        self.stage1_item_click_sound.setSource(QtCore.QUrl.fromLocalFile("assets/stage 1 item clicked.mp3"))

        # stage 1 congrats sound
        self.stage1_congrats_sound_output = QAudioOutput(self)
        self.stage1_congrats_sound = QMediaPlayer(self)
        self.stage1_congrats_sound.setAudioOutput(self.stage1_congrats_sound_output)
        self.stage1_congrats_sound.setSource(QtCore.QUrl.fromLocalFile("assets/congratulations_stage1.mp3"))

        # Quiz_stage right option sound
        self.right_ans_sound_output = QAudioOutput(self)
        self.right_ans_sound = QMediaPlayer(self)
        self.right_ans_sound.setAudioOutput(self.right_ans_sound_output)
        self.right_ans_sound.setSource(QtCore.QUrl.fromLocalFile("assets/right.mp3"))

        # Quiz_stage wrong option sound
        self.wrong_ans_sound_output = QAudioOutput(self)
        self.wrong_ans_sound = QMediaPlayer(self)
        self.wrong_ans_sound.setAudioOutput(self.wrong_ans_sound_output)
        self.wrong_ans_sound.setSource(QtCore.QUrl.fromLocalFile("assets/wrong.mp3"))

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.resize(800, 500)

        # POSITIONING THE GAME WINDOW IN THE CENTER OF THE MONITOR SCREEN
        self.move((self.monitor.width // 2 - self.width() // 2), (self.monitor.height // 2 - self.height() // 2))

        # CREATING TITLE BAR
        self.title_bar = QLabel(" G R E E N   A N D   C L E A N !", self)
        self.title_bar.setStyleSheet('''QLabel
        {background-color: qlineargradient(spread:repeat, x1:0, y1:0, x2:0.266, y2:0.125,
         stop:0 rgba(231, 255, 170, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 10; font: 14pt "Touch Of Nature"; color: green}''')
        self.title_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title_bar.setGeometry(0, 0, self.width(), 35)

        # CODE FOR LEAVES ON THE TITLE BAR
        for i in range(12):
            if i == 6:
                self.leaf_x = self.leaf_x + 422
                self.leaf_file = "assets/basil-right.png"
            i = QLabel(self)
            i.setPixmap(QPixmap(self.leaf_file))
            i.setGeometry(self.leaf_x, self.leaf_y, 30, 30)
            self.leaf_x += 30

        self.body = QLabel(self)
        self.body.setGeometry(0, self.title_bar.height() + 5, self.width(), self.height() - self.title_bar.height() - 5)
        self.body.setStyleSheet("QLabel{background-color: qlineargradient(spread:repeat, x1:0, y1:0, x2:0.266, y2:0.125,\
         stop:0 rgba(231, 255, 170, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 10}")

        # USING THE TRANSPARENT_MASK CLASS TO HELP MOVE THE WINDOW, BUT THE SAME TIME DO NOT HIDE THE TITLE BAR AS IT IS TRANSPARENT.
        self.slayer = transparent_mask(self)
        self.slayer.setGeometry(0, 0, self.title_bar.width(), self.title_bar.height())
        self.slayer.setStyleSheet('''QLabel{border-radius: 10}''')

        ###################################################################################

        ###################################################################################
        # THIS IS THE WELCOME SCENE

        self.logo_pic = QPixmap("assets/logo-transparent.png")
        self.logo_label = QLabel(self)
        self.logo_label.resize(300, 300)
        self.logo_label.setPixmap(QPixmap(self.logo_pic))
        self.logo_label.move((self.width() // 2 - self.logo_label.width() // 2),
                             (self.height() // 2 - self.logo_label.height() // 2))

        opacity_effect = QGraphicsOpacityEffect(self.logo_label)
        self.logo_label.setGraphicsEffect(opacity_effect)

        self.animate_logo = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
        self.animate_logo.setStartValue(0)
        self.animate_logo.setEndValue(1)
        self.animate_logo.setDuration(2000)

        self.disappear_logo = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
        self.disappear_logo.setStartValue(1)
        self.disappear_logo.setEndValue(0)
        self.disappear_logo.setDuration(2000)

        self.full_anim = QtCore.QSequentialAnimationGroup(self)
        self.full_anim.addAnimation(self.animate_logo)
        self.full_anim.addPause(1000)
        self.full_anim.addAnimation(self.disappear_logo)
        self.full_anim.finished.connect(lambda: self.change_intro_text_timer.start(40))
        self.full_anim.start()

        ###################################################################################

        ###################################################################################
        # THIS IS THE INTRODUCTION SCENE.

        self.intro_text = QLabel(self)
        self.intro_text.setGeometry(5, 50, 790, 300)
        self.intro_text.setStyleSheet('''QLabel{font: 26pt "Medula One"}''')
        self.intro_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.skip_btn = QPushButton("Skip", self)
        self.skip_btn.setGeometry(700, 450, 50, 50)
        self.skip_btn.setStyleSheet("QPushButton{font: 20pt 'Medula One'; text-decoration: underline;"
                                    "background-color: rgba(0, 0, 0, 0); color: red}")
        self.skip_btn.clicked.connect(lambda: self.skip_intro_scene())
        self.skip_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.skip_btn.hide()

        self.change_intro_text_timer = QtCore.QTimer(self)
        self.change_intro_text_timer.timeout.connect(lambda: self.change_intro_text())

        self.get_started = QPushButton("Get  Started", self)
        self.get_started.setGeometry(300, 350, 200, 50)
        self.get_started.setStyleSheet(
            "QPushButton{background-color: #Adf802; border-radius: 5; font: 20pt 'Medula One'}"
            "QPushButton:pressed{margin: 1;}")
        self.get_started.clicked.connect(lambda: self.move_to_stage1())
        self.get_started.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.get_started.hide()

        self.get_started_opacity = QGraphicsOpacityEffect(self.get_started)
        self.get_started.setGraphicsEffect(self.get_started_opacity)

        self.anim_btn = QtCore.QPropertyAnimation(self.get_started_opacity, b"opacity")
        self.anim_btn.setStartValue(0)
        self.anim_btn.setEndValue(1)
        self.anim_btn.setDuration(3000)

        ###################################################################################

        ###################################################################################
        # THIS IS STAGE 1
        self.instructor = QLabel(self)
        self.instructor.setGeometry(5, 45, 790, 30)
        self.instructor.setStyleSheet('''QLabel{background-color: white; border: 2px solid black;
                                        border-radius: 5; font: 18pt "Medula One"}''')
        self.instructor.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.instructor.hide()

        self.skip_btn_stage1 = QPushButton("Skip", self)
        self.skip_btn_stage1.setGeometry(715, 45, 75, 26)
        self.skip_btn_stage1.setStyleSheet("QPushButton{font: 18pt 'Medula One'; text-decoration: underline;"
                                           "background-color: rgba(0, 0, 0, 0); color: red;}")
        self.skip_btn_stage1.clicked.connect(lambda: self.skip_stage1_instructs())
        self.skip_btn_stage1.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.skip_btn_stage1.hide()

        self.change_stage1_text_timer = QtCore.QTimer(self)
        self.change_stage1_text_timer.timeout.connect(lambda: self.change_stage1_text())

        self.park_img = QLabel(self)
        self.park_img.setPixmap(QPixmap("assets/park stage 1.jpg"))
        self.park_img.setGeometry(5, 80, 790, 415)
        self.park_img.hide()
        park_opacity = QGraphicsOpacityEffect(self.park_img)
        self.park_img.setGraphicsEffect(park_opacity)

        self.park_mask_img = None

        self.dustbin = QPushButton(self)
        self.dustbin.setGeometry(610, 310, 121, 131)
        self.dustbin.clicked.connect(lambda: self.simple_opacity_animator(self.dustbin, 1, 0, 800, True))
        self.dustbin.clicked.connect(lambda: self.update_item_count())

        self.eaten_apple = QPushButton(self)
        self.eaten_apple.setGeometry(500, 430, 41, 41)
        self.eaten_apple.clicked.connect(lambda: self.simple_opacity_animator(self.eaten_apple, 1, 0, 800, True))
        self.eaten_apple.clicked.connect(lambda: self.update_item_count())

        self.waste_heap = QPushButton(self)
        self.waste_heap.setGeometry(180, 350, 231, 101)
        self.waste_heap.clicked.connect(lambda: self.simple_opacity_animator(self.waste_heap, 1, 0, 800, True))
        self.waste_heap.clicked.connect(lambda: self.update_item_count())

        self.banana = QPushButton(self)
        self.banana.setGeometry(-1, 90, 39, 46)
        self.banana.clicked.connect(lambda: self.simple_opacity_animator(self.banana, 1, 0, 800, True))
        self.banana.clicked.connect(lambda: self.update_item_count())

        self.mud = QPushButton(self)
        self.mud.setGeometry(712, 220, 20, 20)
        self.mud.clicked.connect(lambda: self.simple_opacity_animator(self.mud, 1, 0, 800, True))
        self.mud.clicked.connect(lambda: self.update_item_count())

        self.mud1 = QPushButton(self)
        self.mud1.setGeometry(642, 210, 20, 20)
        self.mud1.clicked.connect(lambda: self.simple_opacity_animator(self.mud1, 1, 0, 800, True))
        self.mud1.clicked.connect(lambda: self.update_item_count())

        self.polythene = QPushButton(self)
        self.polythene.setGeometry(443, 80, 71, 71)
        self.polythene.clicked.connect(lambda: self.simple_opacity_animator(self.polythene, 1, 0, 800, True))
        self.polythene.clicked.connect(lambda: self.update_item_count())

        self.rotten_meat = QPushButton(self)
        self.rotten_meat.setGeometry(250, 250, 71, 71)
        self.rotten_meat.clicked.connect(lambda: self.simple_opacity_animator(self.rotten_meat, 1, 0, 800, True))
        self.rotten_meat.clicked.connect(lambda: self.update_item_count())

        self.waste_tyres = QPushButton(self)
        self.waste_tyres.setGeometry(400, 240, 150, 100)
        self.waste_tyres.clicked.connect(lambda: self.simple_opacity_animator(self.waste_tyres, 1, 0, 800, True))
        self.waste_tyres.clicked.connect(lambda: self.update_item_count())

        self.spoil_oil = QPushButton(self)
        self.spoil_oil.setGeometry(-15, 450, 100, 60)
        self.spoil_oil.clicked.connect(lambda: self.simple_opacity_animator(self.spoil_oil, 1, 0, 800, True))
        self.spoil_oil.clicked.connect(lambda: self.update_item_count())

        self.item_list = [self.park_img, self.dustbin, self.eaten_apple, self.waste_heap, self.banana, self.mud,
                          self.mud1, self.polythene, self.rotten_meat, self.waste_tyres, self.spoil_oil]
        self.item_icon = [None, "assets/garbage.png", "assets/eaten-apple.png",
                          "assets/waste heap.png", "assets/banana.png",
                          "assets/mud.png", "assets/mud.png", "assets/polythene.png",
                          "assets/rotten_meat.png", "assets/waste_tyre.png",
                          "assets/spoil_oil1.png"]

        for i in range(1, len(self.item_list)):
            if not i >= len(self.item_list):
                self.item_list[i].setStyleSheet("QPushButton{background-color: rgba(0, 0, 0, 0)}")
                self.item_list[i].setIcon(QIcon(self.item_icon[i]))
                if self.item_list[i] == self.waste_heap:
                    self.item_list[i].setIconSize(
                        QtCore.QSize(self.item_list[i].width() * 2, self.item_list[i].height() * 2 - 23))
                elif self.item_list[i] == self.banana:
                    self.item_list[i].setIconSize(
                        QtCore.QSize(self.item_list[i].width() + 6, self.item_list[i].height() + 6))
                elif self.item_list[i] == self.waste_tyres:
                    self.item_list[i].setIconSize(
                        QtCore.QSize(self.item_list[i].width() * 2, self.item_list[i].height() * 2 - 50))
                else:
                    self.item_list[i].setIconSize(QtCore.QSize(self.item_list[i].width(), self.item_list[i].height()))
                self.item_list[i].setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                self.item_list[i].hide()

        ###################################################################################

        ###################################################################################
        # INFORMATION STAGE

        self.congrats = QLabel(self)
        self.congrats.setPixmap(QPixmap("assets/congratulations_stage1.png"))
        self.congrats.setGeometry(65, 60, 700, 211)
        self.congrats.hide()

        self.text_msg = QLabel(self)
        self.text_msg.setGeometry(65, 230, 700, 210)
        self.text_msg.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.text_msg.setStyleSheet('''QLabel{font: 20pt 'Medula One'}''')
        self.text_msg.hide()

        self.start_quiz_btn = QPushButton("Start Quiz", self)
        self.start_quiz_btn.setGeometry(355, 450, 100, 35)
        self.start_quiz_btn.setStyleSheet('''QPushButton{border-radius: 10; background-color: #Adf802;
                                            font: 18pt "Medula One"}''')
        self.start_quiz_btn.clicked.connect(lambda: self.quiz_setup())
        self.start_quiz_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.start_quiz_btn.hide()

        self.skip_info_btn = QPushButton("Skip", self)
        self.skip_info_btn.setGeometry(self.skip_btn.geometry())
        self.skip_info_btn.setStyleSheet(self.skip_btn.styleSheet())
        self.skip_info_btn.clicked.connect(lambda: self.skip_info())
        self.skip_info_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.skip_info_btn.hide()

        self.change_info_stage_timer = QtCore.QTimer(self)
        self.change_info_stage_timer.timeout.connect(lambda: self.change_info_stage_text())
        ###################################################################################

        ###################################################################################
        # QUIZ TIME!
        self.op1, self.op2, self.op3, self.op4 = QPushButton(self), QPushButton(self), QPushButton(self), QPushButton(
            self)
        self.op1.setGeometry(60, 260, 250, 40)
        self.op1.clicked.connect(self.check_ans)

        self.op2.setGeometry(490, 260, 250, 40)
        self.op2.clicked.connect(self.check_ans)

        self.op3.setGeometry(60, 350, 250, 40)
        self.op3.clicked.connect(self.check_ans)

        self.op4.setGeometry(490, 350, 250, 40)
        self.op4.clicked.connect(self.check_ans)

        self.ques_label = QLabel(self)
        self.ques_label.setStyleSheet('''QLabel{color: brown; font: 30pt "Medula One"; border: 2px dashed brown;
        border-radius: 10}''')
        self.ques_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ques_label.setGeometry(40, 80, 720, 110)
        self.ques_label.hide()

        self.next_btn = QPushButton("Next", self)
        self.next_btn.setGeometry(365, 450, 70, 30)
        self.next_btn.setStyleSheet(self.start_quiz_btn.styleSheet())
        self.next_btn.clicked.connect(
            lambda: self.move_to_ques(self.ques_list[self.index_no], self.op1_list[self.index_no],
                                      self.op2_list[self.index_no],
                                      self.op3_list[self.index_no], self.op4_list[self.index_no]))
        self.next_btn.hide()

        self.btn_list = [self.op1, self.op2, self.op3, self.op4]
        for i in self.btn_list:
            i.setStyleSheet('''QPushButton{background-color: rgba(0, 0, 0, 0); color: black; border: 2px solid black;
                                border-radius: 5; font: 22pt "Medula One"}''')
            i.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            i.hide()

        self.greet = QLabel(self)
        self.greet.hide()

        self.score = QLabel(self)
        self.score.setGeometry(230, 320, 340, 50)
        self.score.setStyleSheet("QLabel{font: 30pt 'Medula One'}")
        self.score.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.score.hide()

        self.change_knowledge_stage_timer = QtCore.QTimer(self)
        ###################################################################################

        ###################################################################################
        # KNOWLEDGE STAGE
        self.awareness_session = QPushButton("How to make the ecosystem green and clean?", self)
        self.awareness_session.setGeometry(250, 450, 300, 30)
        self.awareness_session.setStyleSheet(self.start_quiz_btn.styleSheet())
        self.awareness_session.clicked.connect(self.move_to_knowledge_scene)
        self.awareness_session.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.awareness_session.hide()

        self.knowledge_text = QLabel(self)
        self.knowledge_text.setGeometry(40, 40, 720, 440)
        self.knowledge_text.setStyleSheet('''QLabel{font: 22pt "Medula One"}''')
        self.knowledge_text.hide()

        self.end_btn = QPushButton("The End!", self)
        self.end_btn.setGeometry(350, 450, 100, 40)
        self.end_btn.setStyleSheet(self.start_quiz_btn.styleSheet())
        self.end_btn.clicked.connect(self.close_game)
        self.end_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.end_btn.hide()
        ###################################################################################

        ###################################################################################
        # FUNCTIONS OF THE GAME

    # This function handles the text animation of intro_text.
    def change_intro_text(self):
        self.skip_btn.show()
        if self.num >= len(self.intro_string):
            self.change_intro_text_timer.stop()
            self.get_started.show()
            self.skip_btn.deleteLater()
            self.anim_btn.start()
            self.num = 0
            self.should_speak = True
        elif self.num == 10 and self.should_speak is True:
            self.speaker.say(self.intro_string.replace("\n", " "))
            self.should_speak = False
        else:
            self.intro_text.setText(self.intro_text.text() + self.intro_string[self.num])
            self.num += 1

    # This function handles the text animation of stage 1.
    def change_stage1_text(self):
        self.instructor.show()
        self.skip_btn_stage1.show()
        if self.stage1_msgs_index >= len(self.stage1_msgs):
            self.change_stage1_text_timer.stop()
            self.num = 0
            self.should_speak = True
            self.instructor.setText(f"{self.stage_item_count} of 10 items removed.")
            self.skip_btn_stage1.deleteLater()
            self.park_mask_img.deleteLater()
            self.stage1_bg_player.play()
        elif self.num >= len(self.current_stage_msg):
            self.should_speak = True
            self.num = 0
            self.stage1_msgs_index += 1
            self.instructor.setText("")
            if not self.stage1_msgs_index >= len(self.stage1_msgs):
                self.current_stage_msg = self.stage1_msgs[self.stage1_msgs_index]
        elif self.num == 6 and self.should_speak is True:
            self.speaker.say(self.current_stage_msg)
            self.should_speak = False
        else:
            self.instructor.setText(self.instructor.text() + self.current_stage_msg[self.num])
            self.num += 1

    # This function will handle the text animation of info stage.
    def change_info_stage_text(self):
        if self.stage1_congrats_sound.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self.text_msg.show()
            self.skip_info_btn.show()
            if self.num >= len(self.info_stage_string):
                self.change_info_stage_timer.stop()
                self.should_speak = True
                self.start_quiz_btn.show()
                self.skip_info_btn.deleteLater()
                self.simple_opacity_animator(self.start_quiz_btn, 0, 1, 1500, False)
            elif self.num == 10 and self.should_speak is True:
                self.speaker.say(self.info_stage_string.replace("\n", " "))
                self.should_speak = False
            else:
                self.text_msg.setText(self.text_msg.text() + self.info_stage_string[self.num])
                self.num += 1

    # Will be used to delay the text animation of info stage.
    def kick_start_changing_info_text(self):
        if self.stage1_congrats_sound.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self.text_msg.show()
            timer = QtCore.QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self.change_info_stage_timer.start(40))
            timer.start(1000)

    # This function will be used to skip the animations of the intro scene
    def skip_intro_scene(self):
        if self.change_intro_text_timer.isActive():
            self.change_intro_text_timer.stop()
            self.get_started.show()
        self.intro_text.setText(self.intro_string)
        self.num = 0
        self.should_speak = True
        self.speaker.stop()
        self.skip_btn.deleteLater()

    # This function will be used to skip the instructions of the stage1 scene
    def skip_stage1_instructs(self):
        if self.change_stage1_text_timer.isActive():
            self.change_stage1_text_timer.stop()
        self.instructor.setText("0 of 10 items removed.")
        self.num = 0
        self.should_speak = True
        self.speaker.stop()
        self.skip_btn_stage1.deleteLater()
        self.park_mask_img.deleteLater()
        self.stage1_bg_player.play()

    # This function will be used to skip the info stage
    def skip_info(self):
        if self.change_info_stage_timer.isActive():
            self.change_info_stage_timer.stop()
        self.speaker.stop()
        self.text_msg.setText(self.info_stage_string)
        self.start_quiz_btn.show()
        self.simple_opacity_animator(self.start_quiz_btn, 0, 1, 1500, False)
        self.skip_info_btn.deleteLater()

    # These functions will run when the get started button of intro_scene is clicked.
    # This will take us to stage 1.
    def dlt_intro_content_and_show_stage1(self):
        self.intro_text.deleteLater()
        self.get_started.deleteLater()
        self.park_img.show()
        for i in self.item_list:
            i.show()

        self.common_opacity_anim_for_stage1(self.item_list, 0, 1, 1500)

        self.park_mask_img = QLabel(self)
        self.park_mask_img.setGeometry(5, 80, 790, 415)
        self.park_mask_img.show()

    # This function will let us move to stage 1 from intro_scene.
    def move_to_stage1(self):
        intro_text_opacity = QGraphicsOpacityEffect(self.intro_text)
        self.intro_text.setGraphicsEffect(intro_text_opacity)

        intro_text_disappear = QtCore.QPropertyAnimation(intro_text_opacity, b"opacity")
        intro_text_disappear.setStartValue(1)
        intro_text_disappear.setEndValue(0)
        intro_text_disappear.setDuration(1500)

        get_started_disappear = QtCore.QPropertyAnimation(self.get_started_opacity, b"opacity")
        get_started_disappear.setStartValue(1)
        get_started_disappear.setEndValue(0)
        get_started_disappear.setDuration(1500)

        parallel_anim = QtCore.QParallelAnimationGroup(self)
        parallel_anim.addAnimation(intro_text_disappear)
        parallel_anim.addAnimation(get_started_disappear)
        parallel_anim.finished.connect(lambda: self.dlt_intro_content_and_show_stage1())
        parallel_anim.start()

    # congrats scene
    def move_to_congrats(self):
        if self.stage1_victory_sound.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self.congrats.show()
            self.simple_opacity_animator(self.congrats, 0, 1, 1500, False)
            self.stage1_congrats_sound.playbackStateChanged.connect(lambda: self.kick_start_changing_info_text())
            self.stage1_congrats_sound.play()
        else:
            self.stage1_victory_sound.playbackStateChanged.connect(lambda: self.move_to_congrats())

    # Function that will be used to create opacity animation for multiple widgets in stage1.
    def common_opacity_anim_for_stage1(self, widget_list: list, start, end, duration):
        anim_group = QtCore.QParallelAnimationGroup(self)
        for i in widget_list:
            a = QGraphicsOpacityEffect(i)
            i.setGraphicsEffect(a)
            anim = QtCore.QPropertyAnimation(a, b"opacity")
            anim.setStartValue(start)
            anim.setEndValue(end)
            anim.setDuration(duration)
            anim_group.addAnimation(anim)
        anim_group.finished.connect(lambda: self.change_stage1_text_timer.start(50))
        anim_group.start()

    # A simple opacity animator so that we do not have to write code for every animation. It can also remove a widget
    # after the animation, which is a very useful thing.

    def simple_opacity_animator(self, widget, start, end, time, dlt: bool):
        anim_group = QtCore.QParallelAnimationGroup(self)
        a = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(a)
        animator = QtCore.QPropertyAnimation(a, b'opacity')
        animator.setStartValue(start)
        animator.setEndValue(end)
        animator.setDuration(time)
        anim_group.addAnimation(animator)
        if dlt:
            anim_group.finished.connect(lambda: widget.deleteLater())
        anim_group.start()

    # Item counting function for stage1, also responsible for playing background sounds in the game.
    def update_item_count(self):
        self.stage_item_count += 1
        self.stage1_item_click_sound.play()
        if self.stage_item_count >= 10:
            self.instructor.setStyleSheet('''QLabel{background-color: white; border: 2px solid black;
                                        border-radius: 5; font: 18pt "Medula One"; color: red}''')
            self.simple_opacity_animator(self.instructor, 1, 0, 1500, True)
            self.simple_opacity_animator(self.park_img, 1, 0, 1500, True)
            self.stage1_bg_player.stop()
            self.stage1_victory_sound.play()
            self.stage1_victory_sound.playbackStateChanged.connect(lambda: self.move_to_congrats())

        self.instructor.setText(f"{self.stage_item_count} of 10 items removed.")

    # Function for setting up the quiz stage.
    def quiz_setup(self):
        self.simple_opacity_animator(self.congrats, 1, 0, 1500, True)
        self.simple_opacity_animator(self.text_msg, 1, 0, 1500, True)
        self.simple_opacity_animator(self.start_quiz_btn, 1, 0, 1500, True)
        self.ques_label.show()
        self.op1.show()
        self.op2.show()
        self.op3.show()
        self.op4.show()
        self.move_to_ques(self.ques_list[self.index_no], self.op1_list[self.index_no], self.op2_list[self.index_no],
                          self.op3_list[self.index_no], self.op4_list[self.index_no])

    # Function for displaying questions and their options and greeting them after the end of the quiz.
    def move_to_ques(self, question, _1, _2, _3, _4):
        if question is not None:
            self.next_btn.hide()
            for i in self.btn_list:
                i.setDisabled(False)
                i.setStyleSheet('''QPushButton{background-color: rgba(0, 0, 0, 0); color: black; border: 2px solid black;
                                                border-radius: 5; font: 22pt "Medula One"}''')
            self.ques_label.setText(question)
            self.op1.setText(_1)
            self.op2.setText(_2)
            self.op3.setText(_3)
            self.op4.setText(_4)
            for i in self.btn_list:
                self.simple_opacity_animator(i, 0, 1, 1500, False)
            self.simple_opacity_animator(self.ques_label, 0, 1, 1500, False)
        else:
            self.greet.show()
            self.score.show()
            self.score.setText(f"Your Score is :  {self.quiz_score}/10")
            self.speaker.setVoice(self.speaker.availableVoices()[0])
            if self.quiz_score == 10:
                self.greet.setGeometry(194, 80, 720, 160)
                self.greet.setPixmap(QPixmap("assets/outstanding1.png"))
                self.speaker.say("Outstanding!")
            elif 10 > self.quiz_score >= 8:
                self.greet.setGeometry(302, 80, 720, 160)
                self.greet.setPixmap(QPixmap("assets/Superb1.png"))
                self.speaker.say("Superb!")
            elif 8 > self.quiz_score >= 6:
                self.greet.setGeometry(262, 80, 720, 160)
                self.greet.setPixmap(QPixmap("assets/Well_done1.png"))
                self.speaker.say("Well Done!")
            elif 6 > self.quiz_score >= 4:
                self.greet.setGeometry(264, 80, 720, 160)
                self.greet.setPixmap(QPixmap("assets/Not-Bad.png"))
                self.speaker.say("Not Bad.")
            elif 4 > self.quiz_score:
                self.greet.setGeometry(300, 80, 720, 160)
                self.greet.setPixmap(QPixmap("assets/alas.png"))
                self.speaker.say("Alas")

            self.simple_opacity_animator(self.op1, 1, 0, 1500, True)
            self.simple_opacity_animator(self.op2, 1, 0, 1500, True)
            self.simple_opacity_animator(self.op3, 1, 0, 1500, True)
            self.simple_opacity_animator(self.op4, 1, 0, 1500, True)
            self.simple_opacity_animator(self.ques_label, 1, 0, 1500, True)
            self.simple_opacity_animator(self.next_btn, 1, 0, 800, True)

            self.awareness_session.show()
            self.simple_opacity_animator(self.greet, 0, 1, 1500, False)
            self.simple_opacity_animator(self.score, 0, 1, 1500, False)
            self.simple_opacity_animator(self.awareness_session, 0, 1, 1500, False)

    # Function for checking if the option chosen is the correct answer.
    def check_ans(self):
        if self.sender().text() == self.correct_answers[self.index_no][self.index_no]:
            self.sender().setStyleSheet(
                '''QPushButton{background-color: #04F404; color: black; border: 2px solid #04F404;
                                border-radius: 5; font: 22pt "Medula One"}''')
            self.right_ans_sound.play()
            self.sender().setDisabled(True)
            self.quiz_score += 1

        else:
            for i in self.btn_list:
                if i.text() != self.correct_answers[self.index_no][self.index_no]:
                    i.setStyleSheet(
                        '''QPushButton{background-color: rgba(0, 0, 0, 0); color: black; border: 2px solid red;
                                    border-radius: 5; font: 22pt "Medula One"}''')
                    i.setDisabled(True)
                else:
                    i.setStyleSheet(
                        '''QPushButton{background-color: #04F404; color: black; border: 2px solid #04F404;
                                    border-radius: 5; font: 22pt "Medula One"}''')
                    i.setDisabled(True)
                    self.wrong_ans_sound.play()

        self.next_btn.show()
        self.index_no += 1

    # Function to switch to the knowledge scene
    def move_to_knowledge_scene(self):
        self.simple_opacity_animator(self.greet, 1, 0, 1500, True)
        self.simple_opacity_animator(self.score, 1, 0, 1500, True)
        self.simple_opacity_animator(self.awareness_session, 1, 0, 1500, True)
        self.knowledge_text.show()
        self.simple_opacity_animator(self.knowledge_text, 0, 1, 1500, False)
        self.change_knowledge_stage_timer.start(50)
        self.change_knowledge_stage_timer.timeout.connect(lambda: self.change_knowledge_text(self.knowledge))
        self.num, self.should_speak = 0, True

    # Function to change the knowledge stage text.
    def change_knowledge_text(self, text):
        if self.num >= len(text):
            self.change_knowledge_stage_timer.stop()
            self.num, self.should_speak = 0, True
            self.end_btn.show()
        elif self.num == 10 and self.should_speak is True:
            self.speaker.say(self.knowledge.replace("\n", " "))
            self.should_speak = False
        else:
            self.knowledge_text.setText(self.knowledge_text.text() + text[self.num])
            self.num += 1

    # Function to close the game window.
    def close_game(self):
        self.speaker.say("The End")
        self.simple_opacity_animator(self, 1, 0, 1500, True)

        ###################################################################################


app = QApplication(argv)
game_window = Game()
game_window.show()

exit(app.exec())
