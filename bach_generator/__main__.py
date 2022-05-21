# -*- coding: utf-8 -*-
"""Main entry point for the music generator"""

import logging
import os
import random
from typing import List

from bach_generator import cli, runner
from bach_generator.src import manager, model


def construct_model_managers(args) -> List[manager.ModelManager]:
    """Constructs model managers or loads them from file"""
    if args.load_filepath:
        model_managers = [
            manager.ModelManager.construct_with_model(model_)
            for model_ in model.load_models(args.load_filepath)
        ]
        return (
            model_managers
            if args.load_best is None
            else model_managers[: args.load_best]
        )

    return [
        manager.ModelManager(
            inputs=args.inputs,
            outputs=1,
            layers=args.layers,
            layer_size=args.layer_size,
        )
        for _ in range(args.models)
    ]


def run_simulation(args):
    """Runs the simulation with the specified command line arguments"""
    model_managers = construct_model_managers(args)
    runner_data = runner.RunnerData(
        generations=args.generations,
        weight_divergence=args.weight_divergence,
        selected_models_per_generation=args.select_models,
        clones_per_model_per_generation=args.clones,
        write_best_model_generation_interval=args.write_interval,
    )

    runner_ = runner.GeneticAlgorithmRunner()
    runner_.setup(input_file=args.filepath, output_directory=args.output_dir)
    evolved_model_managers = runner_.run(model_managers, data=runner_data)

    if args.save:
        filepath = os.path.join(runner_.output_handler.directory, "models.json")
        models = [model_manager.model for model_manager in evolved_model_managers]
        model.save_models(models, filepath)


def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = cli.construct_parser()
    args = parser.parse_args()
    cli.display_args(args)
    random.seed(args.seed)
    run_simulation(args)


main()
