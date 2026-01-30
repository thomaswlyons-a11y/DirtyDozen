import pygame
import random
import sys

# --- CONFIGURATION ---
SCREEN_WIDTH = 1000  # Made wider for text reading
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hangar Havoc: The Dirty Dozen")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)
        
        # Assets
        self.toolbox_rect = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 80, 100, 60)
        
        # Game State Control
        self.state = "SPLASH" # SPLASH, GAME, GAMEOVER
        
        # Initialize Game Variables
        self.reset_game_vars()

    def reset_game_vars(self):
        self.game_over = False
        self.message = ""
        self.score = 0
        self.start_ticks = pygame.time.get_ticks()
        
        # State Flags
        self.fatigue = 0
        self.stress_level = 0 
        self.tool_broken = False 
        self.tunnel_vision = False 
        self.active_popups = [] 
        
        # Create Bolts
        self.bolts = []
        for i in range(6):
            self.bolts.append(Bolt(random.randint(100, 800), random.randint(100, 500)))

    def trigger_random_event(self):
        choice = random.randint(1, 100)
        
        if choice < 5 and not self.tool_broken: 
            self.tool_broken = True 
            self.message = "TOOL BROKE! Visit Toolbox (Lack of Resources)"
            
        elif choice < 10: 
            self.spawn_popup("Distraction")
            
        elif choice < 15:
            self.spawn_popup("Assertiveness")
            
        elif choice < 20:
            self.spawn_popup("Norms")
            
        elif choice < 25:
            self.tunnel_vision = True 
            self.message = "TUNNEL VISION! Right Click to Scan (Lack of Awareness)"
            
        elif choice < 30:
            self.message = "SHIFT CHANGE! Check your work! (Lack of Communication)"
            # Reset 2 random bolts
            if len(self.bolts) > 0:
                for b in random.sample(self.bolts, min(len(self.bolts), 2)):
                    b.is_fixed = False
                    b.progress = 0
                    b.color = YELLOW

        elif choice < 35:
            self.stress_level = 20
            self.message = "STRESS SPIKE! Stop moving to calm down."

    def spawn_popup(self, p_type):
        x = random.randint(200, 600)
        y = random.randint(200, 500)
        self.active_popups.append(Popup(x, y, p_type))

    # --- INPUT HANDLING ---
    def handle_input(self):
        events = pygame.event.get()
        raw_mouse_pos = pygame.mouse.get_pos()
        
        # Apply Stress Jitter in GAME mode only
        if self.state == "GAME" and self.stress_level > 0:
            jitter_x = random.randint(-self.stress_level, self.stress_level)
            jitter_y = random.randint(-self.stress_level, self.stress_level)
            mouse_pos = (raw_mouse_pos[0] + jitter_x, raw_mouse_pos[1] + jitter_y)
        else:
            mouse_pos = raw_mouse_pos

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == "SPLASH":
                    # Press any key to start
                    self.state = "GAME"
                    self.reset_game_vars()
                    self.start_ticks = pygame.time.get_ticks()
                
                elif self.state == "GAMEOVER":
                    if event.key == pygame.K_r:
                        self.state = "SPLASH" # Go back to splash first
                
                elif self.state == "GAME":
                    if event.key == pygame.K_SPACE:
                        self.fatigue = max(0, self.fatigue - 100)
                    if event.key == pygame.K_m:
                        for b in self.bolts:
                            if b.is_mystery:
                                b.is_mystery = False
                                b.color = YELLOW

            if event.type == pygame.MOUSEBUTTONDOWN and self.state == "GAME":
                if event.button == 3: # Right Click
                    self.tunnel_vision = False 
                
                if event.button == 1: # Left Click
                    # Handle Popups
                    popup_hit = False
                    for p in self.active_popups[:]:
                        res = p.handle_click(mouse_pos)
                        if res == "CLOSE":
                            self.active_popups.remove(p)
                            popup_hit = True
                        elif res == "FAIL":
                            self.state = "GAMEOVER"
                            self.message = f"FAIL: {p.fail_msg}"
                            popup_hit = True
                    
                    if not popup_hit:
                        if self.toolbox_rect.collidepoint(mouse_pos):
                            self.tool_broken = False
                            self.message = "Tool Replaced!"

        return mouse_pos

    # --- UPDATE LOOP ---
    def update(self, mouse_pos):
        if self.state != "GAME": return

        # Global Timer (Pressure)
        self.time_left = 60 - (pygame.time.get_ticks() - self.start_ticks) / 1000
        if self.time_left <= 0:
            self.state = "GAMEOVER"
            self.message = "FAIL: Time Out (Pressure)"

        # Random Events
        if random.randint(0, 100) == 1:
            self.trigger_random_event()

        # Fatigue
        self.fatigue += 0.15
        if self.fatigue > 250:
            self.state = "GAMEOVER"
            self.message = "FAIL: Fell Asleep (Fatigue)"

        # Stress Decay
        if self.stress_level > 0 and pygame.mouse.get_rel() == (0,0):
            self.stress_level -= 0.5
        
        # Working on Bolts
        if pygame.mouse.get_pressed()[0] and not self.tool_broken:
            for b in self.bolts:
                if b.rect.collidepoint(mouse_pos) and not b.is_fixed and not b.is_mystery:
                    if b.is_fake_green:
                        b.is_fake_green = False 
                        b.color = YELLOW
                    
                    if b.is_heavy:
                        b.progress += 0.5 
                    else:
                        b.progress += 2.0
                        
                    if b.progress >= 100:
                        b.is_fixed = True
                        b.color = GREEN

        # Win Check
        if all(b.is_fixed for b in self.bolts):
            self.state = "GAMEOVER"
            self.message = "SUCCESS: PLANE AIRWORTHY"

    # --- DRAWING ---
    def draw(self, mouse_pos):
        self.screen.fill(GRAY)

        if self.state == "SPLASH":
            self.draw_splash()
        elif self.state == "GAME":
            self.draw_game(mouse_pos)
        elif self.state == "GAMEOVER":
            self.draw_game(mouse_pos) # Draw game behind overlay
            self.draw_gameover()

        pygame.display.flip()

    def draw_splash(self):
        self.screen.fill(DARK_GRAY)
        
        # Header
        title = self.title_font.render("HANGAR HAVOC: THE DIRTY DOZEN", True, YELLOW)
        t_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, t_rect)
        
        disclaimer = self.font.render("DISCLAIMER: DEMO ONLY. NOT FOR REAL AVIATION TRAINING.", True, RED)
        d_rect = disclaimer.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(disclaimer, d_rect)

        # The Grid of Knowledge
        start_y = 150
        col1_x = 50
        col2_x = SCREEN_WIDTH // 2 + 20
        
        factors = [
            ("1. Lack of Communication", "Don't assume the next shift knows what you did."),
            ("2. Complacency", "Don't sign without looking. Check the Green bolts!"),
            ("3. Lack of Knowledge", "Don't guess on Blue bolts. Press 'M' for Manual."),
            ("4. Distraction", "Ignore the phones! Close pop-ups immediately."),
            ("5. Lack of Teamwork", "Heavy bolts (Purple) need help. Be patient."),
            ("6. Fatigue", "Screen getting dark? Press SPACE to rest."),
            ("7. Lack of Resources", "Tool Broken (Red)? Go to the Toolbox."),
            ("8. Pressure", "You have 60 seconds. Don't panic."),
            ("9. Lack of Assertiveness", "Refuse the Boss. Don't sign unsafe work."),
            ("10. Stress", "Mouse shaking? Stop moving to calm down."),
            ("11. Lack of Awareness", "Tunnel Vision? Right Click to scan."),
            ("12. Norms", "Don't take shortcuts. Follow the rules.")
        ]
        
        for i, (name, desc) in enumerate(factors):
            # Split into two columns
            x = col1_x if i < 6 else col2_x
            y = start_y + (i % 6) * 70
            
            name_surf = self.font.render(name, True, ORANGE)
            desc_surf = self.font_small.render(desc, True, WHITE)
            
            self.screen.blit(name_surf, (x, y))
            self.screen.blit(desc_surf, (x, y + 25))

        # Start Prompt
        prompt = self.large_font.render("PRESS ANY KEY TO START SHIFT", True, GREEN)
        p_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
        
        # Blink effect
        if pygame.time.get_ticks() % 1000 < 500:
            self.screen.blit(prompt, p_rect)

    def draw_game(self, mouse_pos):
        # Draw Toolbox
        color = RED if self.tool_broken else BLACK
        pygame.draw.rect(self.screen, color, self.toolbox_rect)
        tb_text = self.font.render("TOOLBOX", True, WHITE)
        self.screen.blit(tb_text, (self.toolbox_rect.x + 5, self.toolbox_rect.y + 20))

        # Draw Bolts
        for b in self.bolts:
            b.draw(self.screen)

        # Draw Popups
        for p in self.active_popups:
            p.draw(self.screen, self.font)

        # Fatigue Overlay
        if self.fatigue > 0:
            f_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            f_surf.set_alpha(int(self.fatigue))
            f_surf.fill(BLACK)
            self.screen.blit(f_surf, (0,0))

        # Tunnel Vision Overlay
        if self.tunnel_vision:
            mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            mask.fill(BLACK)
            pygame.draw.circle(mask, (30,30,30), mouse_pos, 80)
            mask.set_colorkey((30,30,30))
            self.screen.blit(mask, (0,0))

        # Tool Broken Cursor
        if self.tool_broken:
             pygame.draw.line(self.screen, RED, (mouse_pos[0]-10, mouse_pos[1]-10), (mouse_pos[0]+10, mouse_pos[1]+10), 5)
             pygame.draw.line(self.screen, RED, (mouse_pos[0]+10, mouse_pos[1]-10), (mouse_pos[0]-10, mouse_pos[1]+10), 5)

        # HUD
        timer_col = RED if self.time_left < 15 else WHITE
        time_text = self.large_font.render(f"TIME: {int(self.time_left)}", True, timer_col)
        msg_text = self.font.render(self.message, True, YELLOW)
        self.screen.blit(time_text, (20, 20))
        self.screen.blit(msg_text, (20, 60))

    def draw_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))
        
        color = GREEN if "SUCCESS" in self.message else RED
        text = self.large_font.render(self.message, True, color)
        rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
        restart = self.font.render("Press 'R' to return to Menu", True, WHITE)
        rect2 = restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        
        self.screen.blit(text, rect)
        self.screen.blit(restart, rect2)

class Bolt:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.progress = 0
        self.is_fixed = False
        self.color = YELLOW
        
        self.is_mystery = random.choice([True] + [False]*5) 
        self.is_heavy = random.choice([True] + [False]*8)   
        self.is_fake_green = random.choice([True] + [False]*8) 
        
        if self.is_mystery: self.color = BLUE
        if self.is_heavy: self.color = PURPLE
        if self.is_fake_green: self.color = GREEN

    def draw(self, surface):
        draw_col = self.color
        if self.is_fixed: draw_col = GREEN
        
        pygame.draw.circle(surface, draw_col, self.rect.center, 25)
        pygame.draw.circle(surface, BLACK, self.rect.center, 25, 3)
        
        if self.progress > 0 and not self.is_fixed:
            pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y-10, 50, 8))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y-10, 50 * (self.progress/100), 8))
        
        if self.is_mystery and not self.is_fixed:
            # Draw a small question mark
            pass 

class Popup:
    def __init__(self, x, y, p_type):
        self.rect = pygame.Rect(x, y, 220, 110)
        self.type = p_type
        self.btn1 = pygame.Rect(x+10, y+70, 90, 30) 
        self.btn2 = pygame.Rect(x+120, y+70, 90, 30) 
        
        if self.type == "Distraction":
            self.text = "PHONE RINGING!"
            self.sub = "Answer it?"
            self.l1, self.l2 = "Answer", "Ignore"
            self.fail_msg = "Distracted by Phone"
        elif self.type == "Assertiveness":
            self.text = "BOSS: SIGN IT NOW!"
            self.sub = "It's not safe..."
            self.l1, self.l2 = "Sign", "Refuse" 
            self.fail_msg = "Bullied by Boss"
        elif self.type == "Norms":
            self.text = "SHORTCUT FOUND!"
            self.sub = "Skip procedure?"
            self.l1, self.l2 = "Yes", "No" 
            self.fail_msg = "Normalized Deviance"

    def draw(self, surface, font):
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 3)
        
        t1 = font.render(self.text, True, RED)
        t2 = font.render(self.sub, True, BLACK)
        surface.blit(t1, (self.rect.x + 10, self.rect.y + 10))
        surface.blit(t2, (self.rect.x + 10, self.rect.y + 35))
        
        pygame.draw.rect(surface, GRAY, self.btn1)
        pygame.draw.rect(surface, GRAY, self.btn2)
        
        l1_txt = font.render(self.l1, True, WHITE)
        l2_txt = font.render(self.l2, True, WHITE)
        surface.blit(l1_txt, (self.btn1.x+5, self.btn1.y+5))
        surface.blit(l2_txt, (self.btn2.x+5, self.btn2.y+5))

    def handle_click(self, pos):
        if self.btn1.collidepoint(pos):
            # Button 1 is always the WRONG choice in this design
            return "FAIL"
        if self.btn2.collidepoint(pos):
            # Button 2 is always the RIGHT choice
            return "CLOSE"
        return "NONE"

# --- MAIN LOOP ---
if __name__ == "__main__":
    game = Game()
    while True:
        m_pos = game.handle_input()
        game.update(m_pos)
        game.draw(m_pos)
        game.clock.tick(FPS)
