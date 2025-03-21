import pygame
import random
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_files = [
            os.path.join('assets', 'music', track) for track in os.listdir('assets/music')]

    def play_random_music(self):
        if not pygame.mixer.music.get_busy():
            self.current_track = random.choice(self.music_files)
            pygame.mixer.music.load(self.current_track)
            pygame.mixer.music.play()

    @staticmethod
    def stop():
        pygame.mixer.music.stop()