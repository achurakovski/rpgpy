import random

class Spell:
    def __init__(self, name, mana_cost, effect_type):
        self.name = name
        self.mana_cost = mana_cost
        self.effect_type = effect_type

class Spellbook:
    def __init__(self):
        all_available_spells = [
            Spell("Frost shield", 25, 'armor'),
            Spell("Mist coil", 50, 'damage_heal'),
            Spell("Bloodrage", 40, 'global_damage_buff')
        ]
        self.spells = random.sample(all_available_spells, 2)

    def get_affordable_spells(self, current_mana):
        return [spell for spell in self.spells if spell.mana_cost <= current_mana]

class Hero:
    def __init__(self, name, hp, armor=0, damage=0, evasion=0.0):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.base_armor = armor
        self.damage = damage
        self.evasion = evasion
        self.owner = None
        self.buffs = []

    def is_alive(self):
        return self.hp > 0

    def get_total_armor(self):
        bonus_armor = sum(buff['amount'] for buff in self.buffs if buff['type'] == 'armor')
        return self.base_armor + bonus_armor

    def take_damage(self, amount):
        if random.random() < self.evasion:
            print(f"  💨 {self.name} виртуозно уклоняется от атаки! (Урон: 0)")
            return

        total_armor = self.get_total_armor()
        damage_reduction = min(total_armor * 0.10, 1.0)
        final_damage = int(amount * (1 - damage_reduction))
        
        self.hp = max(0, self.hp - final_damage)
        blocked = amount - final_damage
        
        print(f"  ⚔️ {self.name} получает {final_damage} урона (Броня поглотила {blocked}). Осталось ХП: {self.hp}")
        
        if not self.is_alive():
            print(f"  ☠️ {self.name} погибает в пылу сражения!")

    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        print(f"  💚 {self.name} исцелен на {self.hp - old_hp}. Текущее ХП: {self.hp}")

    def update_buffs(self):
        for buff in self.buffs:
            buff['turns'] -= 1
        self.buffs = [buff for buff in self.buffs if buff['turns'] > 0]

    def act(self, all_heroes):
        pass

class Warrior(Hero):
    def __init__(self, name, hp, damage):
        super().__init__(name, hp, armor=2, damage=damage)

    def act(self, all_heroes):
        enemies = [h for h in all_heroes if h.owner != self.owner and h.is_alive()]
        if enemies:
            target = random.choice(enemies)
            base_damage = random.randint(self.damage - 5, self.damage + 5)
            
            if random.random() <= 0.20:
                final_damage = int(base_damage * 1.5)
                print(f"🗡️ [КРИТ!] Воин {self.name} яростно атакует {target.name} на {final_damage} урона!")
            else:
                final_damage = base_damage
                print(f"🗡️ Воин {self.name} атакует {target.name} на {final_damage} урона.")
                
            target.take_damage(final_damage)

class Archer(Hero):
    def __init__(self, name):
        super().__init__(name, hp=150, armor=1, damage=30, evasion=0.20)

    def act(self, all_heroes):
        enemies = [h for h in all_heroes if h.owner != self.owner and h.is_alive()]
        if enemies:
            target = random.choice(enemies)
            actual_damage = random.randint(self.damage - 5, self.damage + 5)
            print(f"🏹 Лучник {self.name} совершает меткий выстрел в {target.name} на {actual_damage} урона!")
            target.take_damage(actual_damage)

class Magician(Hero):
    def __init__(self, name):
        super().__init__(name, hp=200, armor=0, damage=0) 
        self.mana = 300
        self.spellbook = Spellbook()

    def act(self, all_heroes):
        alive_heroes = [h for h in all_heroes if h.is_alive()]
        affordable_spells = self.spellbook.get_affordable_spells(self.mana)

        if not affordable_spells:
            print(f"💤 Маг {self.name} пропускает ход (осталось {self.mana} маны).")
            return

        spell = random.choice(affordable_spells)
        self.mana -= spell.mana_cost

        if spell.effect_type == 'global_damage_buff':
            print(f"✨ Маг {self.name} кастует '{spell.name}'! (-{spell.mana_cost} маны). Все выжившие герои получают +5 к урону!")
            for hero in alive_heroes:
                hero.damage += 5
            return

        target = random.choice(alive_heroes)
        print(f"✨ Маг {self.name} применяет '{spell.name}' на {target.name} (-{spell.mana_cost} маны).")

        if spell.effect_type == 'armor':
            target.buffs.append({'type': 'armor', 'amount': 2, 'turns': 2})
            print(f"  🛡️ {target.name} получает +2 брони на 2 хода!")
            
        elif spell.effect_type == 'damage_heal':
            if target.owner == self.owner:
                target.heal(75)
            else:
                target.take_damage(50)

class Player:
    def __init__(self, name, heroes):
        self.name = name
        self.heroes = heroes
        for hero in self.heroes:
            hero.owner = self
            hero.name = f"[{self.name}] {hero.name}"

    def is_alive(self):
        return any(hero.is_alive() for hero in self.heroes)

class Battle:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def start(self):
        print(f"🔥 НАЧИНАЕТСЯ СМЕРТЕЛЬНАЯ БИТВА: {self.p1.name} VS {self.p2.name} 🔥\n")
        round_number = 1

        while self.p1.is_alive() and self.p2.is_alive():
            print(f"=== РАУНД {round_number} ===")
            
            all_alive = [h for h in self.p1.heroes + self.p2.heroes if h.is_alive()]
            random.shuffle(all_alive)

            for hero in all_alive:
                if not hero.is_alive():
                    continue
                
                if not self.p1.is_alive() or not self.p2.is_alive():
                    break 

                hero.update_buffs()
                hero.act(self.p1.heroes + self.p2.heroes)
                
            print("") 
            round_number += 1

        print("=============================")
        if self.p1.is_alive():
            print(f"🏆 ПОБЕДИТЕЛЬ: {self.p1.name}!")
        else:
            print(f"🏆 ПОБЕДИТЕЛЬ: {self.p2.name}!")
        print("=============================")

if __name__ == "__main__":
    team1 = [
        Warrior("Артур", hp=250, damage=35),
        Archer("Леголас"),
        Magician("Мерлин")
    ]
    player1 = Player("Player 1", team1)

    team2 = [
        Warrior("Конан", hp=220, damage=40),
        Archer("Робин"),
        Magician("Гендальф")
    ]
    player2 = Player("Player 2", team2)

    battle = Battle(player1, player2)
    battle.start()
