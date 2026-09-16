import random

# --- МЕХАНИКА ЗАКЛИНАНИЙ ---

class Spell:
    def __init__(self, name, mana_cost, effect_type):
        self.name = name
        self.mana_cost = mana_cost
        self.effect_type = effect_type

class Spellbook:
    def __init__(self):
        # База из трех возможных заклинаний
        all_available_spells = [
            Spell("Магический панцирь", 25, 'armor'),
            Spell("Длань судьбы", 50, 'damage_heal'),
            Spell("Жажда крови", 40, 'global_damage_buff')
        ]
        # Маг получает 2 случайных заклинания из 3 при создании
        self.spells = random.sample(all_available_spells, 2)

    def get_affordable_spells(self, current_mana):
        return [spell for spell in self.spells if spell.mana_cost <= current_mana]

# --- БАЗОВЫЙ КЛАСС ЮНИТА ---

class Unit:
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
        # Механика уклонения
        if random.random() < self.evasion:
            print(f"  💨 {self.name} виртуозно уклоняется от атаки! (Урон: 0)")
            return

        total_armor = self.get_total_armor()
        # 1 ед. брони = 10% снижения урона
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

    def act(self, all_units):
        pass

# --- КЛАССЫ БОЙЦОВ ---

class Warrior(Unit):
    def __init__(self, name, hp, damage):
        # У воина по умолчанию 2 брони
        super().__init__(name, hp, armor=2, damage=damage)

    def act(self, all_units):
        enemies = [u for u in all_units if u.owner != self.owner and u.is_alive()]
        if enemies:
            target = random.choice(enemies)
            base_damage = random.randint(self.damage - 5, self.damage + 5)
            
            # Шанс 20% на критический удар (150% урона)
            if random.random() <= 0.20:
                final_damage = int(base_damage * 1.5)
                print(f"🗡️ [КРИТ!] Воин {self.name} яростно атакует {target.name} на {final_damage} урона!")
            else:
                final_damage = base_damage
                print(f"🗡️ Воин {self.name} атакует {target.name} на {final_damage} урона.")
                
            target.take_damage(final_damage)

class Archer(Unit):
    def __init__(self, name):
        # У лучника 150 ХП, 30 урона, 1 броня и 20% уклонения
        super().__init__(name, hp=150, armor=1, damage=30, evasion=0.20)

    def act(self, all_units):
        enemies = [u for u in all_units if u.owner != self.owner and u.is_alive()]
        if enemies:
            target = random.choice(enemies)
            actual_damage = random.randint(self.damage - 5, self.damage + 5)
            print(f"🏹 Лучник {self.name} совершает меткий выстрел в {target.name} на {actual_damage} урона!")
            target.take_damage(actual_damage)

class Magician(Unit):
    def __init__(self, name):
        # Магу фиксируем 200 ХП, без брони. Манапул 300.
        super().__init__(name, hp=200, armor=0, damage=0) 
        self.mana = 300
        self.spellbook = Spellbook()

    def act(self, all_units):
        alive_units = [u for u in all_units if u.is_alive()]
        affordable_spells = self.spellbook.get_affordable_spells(self.mana)

        if not affordable_spells:
            print(f"💤 Маг {self.name} пропускает ход (осталось {self.mana} маны).")
            return

        spell = random.choice(affordable_spells)
        self.mana -= spell.mana_cost

        # Обработка глобального заклинания
        if spell.effect_type == 'global_damage_buff':
            print(f"✨ Маг {self.name} кастует '{spell.name}'! (-{spell.mana_cost} маны). Все выжившие герои получают +5 к урону!")
            for unit in alive_units:
                unit.damage += 5
            return

        # Обработка таргетных заклинаний
        target = random.choice(alive_units)
        print(f"✨ Маг {self.name} применяет '{spell.name}' на {target.name} (-{spell.mana_cost} маны).")

        if spell.effect_type == 'armor':
            target.buffs.append({'type': 'armor', 'amount': 2, 'turns': 2})
            print(f"  🛡️ {target.name} получает +2 брони на 2 хода!")
            
        elif spell.effect_type == 'damage_heal':
            if target.owner == self.owner:
                target.heal(75)
            else:
                target.take_damage(50)

# --- ИГРОК И МЕНЕДЖЕР БОЯ ---

class Player:
    def __init__(self, name, units):
        self.name = name
        self.units = units
        for unit in self.units:
            unit.owner = self
            unit.name = f"[{self.name}] {unit.name}"

    def is_alive(self):
        return any(unit.is_alive() for unit in self.units)

class Battle:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def start(self):
        print(f"🔥 НАЧИНАЕТСЯ СМЕРТЕЛЬНАЯ БИТВА: {self.p1.name} VS {self.p2.name} 🔥\n")
        round_number = 1

        while self.p1.is_alive() and self.p2.is_alive():
            print(f"=== РАУНД {round_number} ===")
            
            # Все живые юниты собираются и перемешиваются для случайной инициативы
            all_alive = [u for u in self.p1.units + self.p2.units if u.is_alive()]
            random.shuffle(all_alive)

            for unit in all_alive:
                if not unit.is_alive():
                    continue
                
                if not self.p1.is_alive() or not self.p2.is_alive():
                    break 

                unit.update_buffs()
                unit.act(self.p1.units + self.p2.units)
                
            print("") 
            round_number += 1

        # Финал
        print("=============================")
        if self.p1.is_alive():
            print(f"🏆 ПОБЕДИТЕЛЬ: {self.p1.name}!")
        else:
            print(f"🏆 ПОБЕДИТЕЛЬ: {self.p2.name}!")
        print("=============================")

# --- ТЕСТОВЫЙ ЗАПУСК ---

if __name__ == "__main__":
    # Команда 1
    team1 = [
        Warrior("Артур", hp=250, damage=35),
        Archer("Леголас"),
        Magician("Мерлин")
    ]
    player1 = Player("Синие", team1)

    # Команда 2
    team2 = [
        Warrior("Конан", hp=220, damage=40),
        Archer("Робин"),
        Magician("Гендальф")
    ]
    player2 = Player("Красные", team2)

    # Запуск
    battle = Battle(player1, player2)
    battle.start()
