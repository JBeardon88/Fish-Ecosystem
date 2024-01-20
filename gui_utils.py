import pygame

def draw_text(screen, text, position, font, color=(255, 255, 255)):
    """
    Draws text on the Pygame screen.

    :param screen: Pygame screen where to draw
    :param text: Text to be drawn
    :param position: Tuple (x, y) position of the text on the screen
    :param font: Pygame font used for the text
    :param color: Color of the text (default is white)
    """
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def draw_button(screen, text, position, size, font, button_color, text_color, padding=10):
    """
    Draws a button with text on the Pygame screen, with added padding.

    :param padding: Padding around the text within the button.
    """
    # Calculate text surface with padding
    text_surface = font.render(text, True, text_color)
    text_width_with_padding = text_surface.get_width() + 2 * padding
    text_height_with_padding = text_surface.get_height() + 2 * padding
    
    # Adjust button size if text is too wide
    if text_width_with_padding > size[0]:
        size = (text_width_with_padding, size[1])
    
    # Draw button rectangle
    pygame.draw.rect(screen, button_color, (*position, *size))
    
    # Blit the text surface onto the screen at the centered position
    text_x = position[0] + (size[0] - text_surface.get_width()) // 2
    text_y = position[1] + (size[1] - text_surface.get_height()) // 2
    screen.blit(text_surface, (text_x, text_y))


def is_button_clicked(mouse_pos, button_pos, button_size):
    """
    Checks if a button is clicked based on the mouse position.

    :param mouse_pos: Tuple (x, y) position of the mouse click
    :param button_pos: Tuple (x, y) position of the button
    :param button_size: Tuple (width, height) size of the button
    :return: Boolean indicating if the button is clicked
    """
    x, y = mouse_pos
    bx, by, bw, bh = button_pos[0], button_pos[1], button_size[0], button_size[1]
    return bx <= x <= bx + bw and by <= y <= by + bh
