from lib2d.game import Game
from lib2d import gfx, context
import pygame


profile = 1


class TestGame(Game):
    def start(self):
        from lib.physicstest import PhysicsTest
        gfx.set_screen((1024, 600), 4, "scale")
        self.sd = context.ContextDriver(self, [], 60)
        self.sd.reload_screen()
        self.sd.start(PhysicsTest(self.sd))
        self.sd.run()


if __name__ == "__main__":
    if profile:
        import cProfile
        import pstats
        import sys

        game = TestGame()
        cProfile.run('game.start()', "results.prof")

        p = pstats.Stats("results.prof")
        p.strip_dirs()
        p.sort_stats('time').print_stats(20, "^((?!pygame).)*$")
        p.sort_stats('time').print_stats(20)

    else:
        TestGame().start()

    pygame.quit()
