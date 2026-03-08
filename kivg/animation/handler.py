"""
AnimationHandler manages animation creation and sequencing.

This module provides utilities for combining animations, adding fill effects,
and managing the animation lifecycle.
"""

from typing import List, Any, Optional, Callable

from kivg.animation.kivy_animation import Animation
from kivg.data_classes import AnimationContext
from kivg.animation.animation_shapes import ShapeAnimator
from kivg.constants import (
    DEFAULT_FILL_ANIMATION_DURATION,
    MESH_OPACITY_PROPERTY,
    DEFAULT_TRANSITION
)


class AnimationHandler:
    """
    Centralized handler for all types of animations in Kivg.
    
    Provides utilities for creating animation sequences, adding fill animations,
    and managing animation lifecycle (start, bind callbacks, cancel).
    """
    
    @staticmethod
    def create_animation_sequence(animations: List[Animation], 
                                 sequential: bool = True) -> Optional[Animation]:
        """
        Create a sequence or parallel animation from multiple animations.
        
        Combines multiple Animation objects using either sequential (+) or
        parallel (&) operators.
        
        Args:
            animations: List of Animation objects to combine
            sequential: If True, animations run one after another (A + B);
                       if False, animations run simultaneously (A & B)
            
        Returns:
            Combined Animation object, or None if animations list is empty
            
        Example:
            >>> anim1 = Animation(d=0.5, x=100)
            >>> anim2 = Animation(d=0.5, y=200)
            >>> seq = AnimationHandler.create_animation_sequence([anim1, anim2], True)
            >>> # Runs anim1, then anim2
        """
        if not animations:
            return None
            
        combined = animations[0]
        for anim in animations[1:]:
            if sequential:
                combined += anim  # Sequential: runs one after another
            else:
                combined &= anim  # Parallel: runs simultaneously
                
        return combined
    
    @staticmethod
    def add_fill_animation(anim: Animation, widget: Any, 
                          on_progress_callback: Optional[Callable] = None) -> Animation:
        """
        Add a fade-in animation for shape filling.
        
        Appends a mesh opacity animation to create a fill effect after
        the drawing animation completes.
        
        Args:
            anim: Base animation to add fill animation to
            widget: Widget to animate
            on_progress_callback: Optional callback function for animation progress updates
            
        Returns:
            Combined Animation with fill effect added (runs sequentially)
            
        Example:
            >>> draw_anim = Animation(d=1.0, x=100)
            >>> full_anim = AnimationHandler.add_fill_animation(draw_anim, widget)
            >>> # Draws path, then fades in fill
        """
        fill_anim = Animation(d=DEFAULT_FILL_ANIMATION_DURATION, 
                            **{MESH_OPACITY_PROPERTY: 1})
        
        if on_progress_callback:
            fill_anim.bind(on_progress=on_progress_callback)
            
        return anim + fill_anim
    
    @staticmethod
    def prepare_and_start_animation(
        anim: Animation, 
        widget: Any, 
        on_progress_callback: Optional[Callable] = None,
        on_complete_callback: Optional[Callable] = None
    ) -> None:
        """
        Prepare and start an animation with optional callbacks.
        
        Cancels any existing animations on the widget, binds callbacks if provided,
        and starts the new animation.
        
        Args:
            anim: Animation object to start
            widget: Widget to animate
            on_progress_callback: Optional function called on each animation frame
                                 Signature: callback(animation, widget, progression)
            on_complete_callback: Optional function called when animation completes
                                Signature: callback(animation, widget)
                                
        Example:
            >>> anim = Animation(d=1.0, x=100)
            >>> def on_done(anim, widget):
            ...     print("Animation complete!")
            >>> AnimationHandler.prepare_and_start_animation(anim, widget, on_complete_callback=on_done)
        """
        anim.cancel_all(widget)
        
        if on_progress_callback:
            anim.bind(on_progress=on_progress_callback)
            
        if on_complete_callback:
            anim.bind(on_complete=on_complete_callback)
            
        anim.start(widget)
    
    @staticmethod
    def setup_shape_animations(
        caller: Any,
        context: AnimationContext
    ) -> List[Animation]:
        """
        Set up animations for a shape using ShapeAnimator.
        
        Args:
            caller: The caller object (usually Kivg instance)
            context: AnimationContext with animation parameters
            
        Returns:
            List of Animation objects
        """
        return ShapeAnimator.setup_animation(caller, context)
        
    @staticmethod
    def prepare_shape_animations(
        caller: Any,
        widget: Any,
        anim_config_list: List[Dict],
        closed_shapes: OrderedDict,
        svg_size: List[float],
        svg_file: str
    ) -> List[Tuple[str, Animation]]:
        """
        Prepare animations for shapes based on configuration list.
        
        Creates AnimationContext objects from config and delegates to
        ShapeAnimator for actual animation setup.
        
        Args:
            caller: Object calling the animation (typically Kivg instance)
            widget: Kivy widget to animate
            anim_config_list: List of animation configuration dictionaries, each with:
                            - id_: Shape ID (required)
                            - from_: Direction ("left", "right", "top", "bottom", etc.)
                            - d: Duration in seconds (default: 0.3)
                            - t: Transition type (default: "out_sine")
            closed_shapes: OrderedDict of SVG path data organized by shape ID
            svg_size: SVG dimensions [width, height]
            svg_file: Path to the SVG file
            
        Returns:
            List of (shape_id, Animation) tuples for each configured shape
            
        Example:
            >>> config = [{"id_": "shape1", "from_": "left", "d": 0.5}]
            >>> anims = AnimationHandler.prepare_shape_animations(
            ...     kivg, widget, config, shapes, [100, 100], "icon.svg"
            ... )
        """
        animation_list = []
        
        for config in anim_config_list:
            # Create animation context
            context = AnimationContext(
                widget=widget,
                shape_id=config["id_"],
                direction=config.get("from_", None),
                transition=config.get("t", DEFAULT_TRANSITION),
                duration=config.get("d", 0.3),
                closed_shapes=closed_shapes,
                sw_size=svg_size,
                svg_file=svg_file
            )
            
            # Get animation list from ShapeAnimator
            anim_list = AnimationHandler.setup_shape_animations(caller, context)
            
            if anim_list:
                # Combine animations in parallel
                combined_anim = AnimationHandler.create_animation_sequence(
                    anim_list, sequential=False
                )
                animation_list.append((config["id_"], combined_anim))
                
        return animation_list
