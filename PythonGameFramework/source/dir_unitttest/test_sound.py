'''
Created on Feb 26, 2017

@author: Robert
'''
import unittest
from sound import SoundWrapper
from setup import soundPlayerFactory
import parameters as PRAM
import pygame

class TestSoundPlayers(unittest.TestCase):

    def setUp(self):
        pygame.init()  # @UndefinedVariable
        self.musicPlayer, self.soundPlayer = soundPlayerFactory()
        
### MusicPlayer() ###
    def test_loadSong(self):
        self.assertEqual(self.musicPlayer.loadSong(SoundWrapper('notsong', PRAM.MUSIC_PATH, PRAM.SONG_TEST, '.mp3')), False)
        self.assertEqual(self.musicPlayer.loadSong(SoundWrapper('song', PRAM.MUSIC_PATH, PRAM.SONG_TEST, '.mp3')), True)
        self.assertEqual(self.musicPlayer.loadSong(SoundWrapper('song', PRAM.MUSIC_PATH, 'songnotfound', '.mp3')), False)
        self.assertEqual(self.musicPlayer.loadSong(SoundWrapper('song', PRAM.MUSIC_PATH, PRAM.SONG_TEST, '.mp3')), False) #already loaded
        
    def test_playSong(self):
        self.assertEqual(self.musicPlayer.playSong(PRAM.SONG_TEST), True)
        self.assertEqual(self.musicPlayer.playSong('songnotfound'), False)
        self.assertEqual(self.musicPlayer.playSong(PRAM.SONG_TEST,1), True) #play song once              
        self.assertEqual(self.musicPlayer.playSong(PRAM.SONG_ERROR), True) #play error song
### soundPlayer() ###
    def test_loadSound(self):
        self.assertEqual(self.soundPlayer.loadSound(SoundWrapper('notsound', PRAM.SOUND_PATH, PRAM.SOUND_TEST, '.wav')), False)
        self.assertEqual(self.soundPlayer.loadSound(SoundWrapper('sound', PRAM.SOUND_PATH, PRAM.SOUND_TEST, '.wav')), True)
        self.assertEqual(self.soundPlayer.loadSound(SoundWrapper('sound', PRAM.SOUND_PATH, 'effectnotfound', '.wav')), False)
        self.assertEqual(self.soundPlayer.loadSound(SoundWrapper('sound', PRAM.SOUND_PATH, PRAM.SOUND_TEST, '.wav')), False) #already loaded

    def test_playSound(self):
        self.assertEqual(self.soundPlayer.playSound(PRAM.SOUND_TEST), True)
        self.assertEqual(self.soundPlayer.playSound('effectnotfound'), False)            
          
    def test_setSoundVolume(self):
        self.assertEqual(self.soundPlayer.setSoundVolume(PRAM.SOUND_TEST,0), True)
        self.assertEqual(self.soundPlayer.setSoundVolume(PRAM.SOUND_TEST,0.62), True)  
        self.assertEqual(self.soundPlayer.setSoundVolume(PRAM.SOUND_TEST,1.0), True)                           
        self.assertEqual(self.soundPlayer.setSoundVolume(PRAM.SOUND_TEST,1.001), False) 
        self.assertEqual(self.soundPlayer.setSoundVolume(PRAM.SOUND_TEST,-1.0), False)       
        self.assertEqual(self.soundPlayer.setSoundVolume('effectnotfound',5), False) 
        self.assertEqual(self.soundPlayer.setSoundVolume('effectnotfound',0.5), False) 
          
    def tearDown(self):
        pass
#         self.musicPlayer.dispose()
#         self.soundPlayer.dispose()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()