import random
import augraphy as aug

def get_augment_pipeline(probability):
    ink_phase = [
        aug.OneOf(
            [
                aug.Dithering(
                    p=probability/4
                    ),
                aug.BleedThrough(
                    intensity_range=(0.05, 0.1),  # Reduced intensity
                    color_range=(64, 192),  # Narrower color range for less intensity
                    alpha=random.uniform(0.05, 0.1),  # Reduced alpha
                    offsets=(5, 10),  # Reduced offsets
                    p=probability/4,
                    ),
                aug.InkBleed(
                    intensity_range=(0.2, 0.3),  # Reduced intensity
                    kernel_size=random.choice([(1, 1), (3, 3)]),
                    severity=(0.1, 0.2),  # Reduced severity
                    p=probability/4
                    )
            ],
            p=probability/2
            )
        ]
    
    paper_phase = [
        aug.ColorPaper(p=probability/10),
        aug.OneOf(
            [
                aug.DelaunayTessellation(
                    p=probability/3
                ),
                aug.PatternGenerator(
                    alpha_range=(0.1, 0.25),  # Reduced alpha range
                    p=probability/3
                ),
                aug.VoronoiTessellation(
                    p=probability/3
                ),
            ], 
            p=probability/2),
        aug.AugmentationSequence([
                aug.NoiseTexturize(
                    sigma_range=(1, 5),  # Reduced sigma range
                    turbulence_range=(1, 3),  # Reduced turbulence range
                    p=probability/2),  
                aug.BrightnessTexturize(
                    texturize_range=(0.95, 0.99),  # Narrower range for less brightness variation
                    deviation=0.01,  # Reduced deviation
                    p=probability/2)
                    ])
        ]

    post_phase = [
        aug.OneOf(
            [
                aug.DirtyDrum(
                    line_width_range=(1, 3),  # Narrower line width range
                    line_concentration=random.uniform(0.02, 0.05),  # Reduced concentration
                    direction=random.randint(0, 2),  # Fewer directions
                    noise_intensity=random.uniform(0.3, 0.5),  # Reduced noise intensity
                    noise_value=(128, 192),  # Narrower noise value range
                    ksize=random.choice([(3, 3)]),  # Smaller kernel size
                    sigmaX=0,
                    p=probability/4,
                ),
                aug.DirtyRollers(
                    line_width_range=(1, 16),  # Reduced line width range
                    scanline_type=0,
                ),
            ],
            p=probability/4,
        ),
        aug.SubtleNoise(
            subtle_range=random.randint(1, 5),  # Reduced subtle range
            p=probability/4,
        ),
        aug.Jpeg(
            quality_range=(50, 95),  # Higher minimum quality
            p=probability/2,
        ),
        aug.OneOf(
            [
                aug.Markup(
                    num_lines_range=(1, 3),  # Fewer lines
                    markup_length_range=(0.25, 0.5),  # Shorter lines
                    markup_thickness_range=(1, 2),  # Thinner lines
                    markup_type=random.choice(["strikethrough", "crossed", "highlight", "underline"]),
                    markup_color="random",
                    single_word_mode=False,
                    repetitions=1,
                ),
                aug.Scribbles(
                    scribbles_type="random",
                    scribbles_location="random",
                    scribbles_size_range=(100, 300),  # Smaller scribbles
                    scribbles_count_range=(1, 3),  # Fewer scribbles
                    scribbles_thickness_range=(1, 3),
                    scribbles_brightness_change=[32, 64],
                    scribbles_text="random",
                    scribbles_text_font="random",
                    scribbles_text_rotate_range=(0, 180),  # Reduced rotation range
                    scribbles_lines_stroke_count_range=(1, 3),  # Fewer strokes
                ),
            ],
            p=probability/4,
        ),
        aug.ColorShift(
            color_shift_offset_x_range=(1, 2),  # Smaller offsets
            color_shift_offset_y_range=(1, 2),  # Smaller offsets
            color_shift_iterations=(1, 2),  # Fewer iterations
            color_shift_brightness_range=(0.95, 1.05),  # Narrower brightness range
            color_shift_gaussian_kernel_range=(3, 3),
            p=probability/4,
        ),
        aug.BadPhotoCopy(
            noise_type=-1,
            noise_side="random",
            noise_iteration=(1, 1),  # Single iteration
            noise_size=(1, 2),  # Smaller noise size
            noise_value=(160, 196),  # Narrower noise value range
            noise_sparsity=(0.1, 0.3),  # Reduced sparsity
            noise_concentration=(0.05, 0.3),  # Reduced concentration
            blur_noise=random.choice([True, False]),
            blur_noise_kernel=random.choice([(3, 3), (5, 5)]),
            wave_pattern=random.choice([True, False]),
            edge_effect=random.choice([True, False]),
        ),
        aug.Faxify(
            scale_range=(0.1, 0.3),  # Smaller scale range
            monochrome=random.choice([0, 1]),
            monochrome_method="random",
            monochrome_arguments={},
            halftone=random.choice([0, 1]),
            invert=1,
            half_kernel_size=random.choice([(1, 1), (2, 2)]),
            angle=(0, 180),  # Reduced angle range
            sigma=(1, 3),
            p=probability/3,
        ),
        ]

    pipeline = aug.AugraphyPipeline(ink_phase, paper_phase, post_phase)

    return pipeline