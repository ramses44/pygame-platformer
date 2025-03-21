from abc import ABC, abstractmethod


class Scene(ABC):
    @abstractmethod
    def handle_event(self, event):
        ...
    
    @abstractmethod
    def update(self):
        ...
    
    @abstractmethod
    def draw(self, screen):
        ...

    def format_time(self, seconds):
        if not seconds:
            return "--:--"
        return f"{int(seconds // 60):02}:{int(seconds % 60):02}"