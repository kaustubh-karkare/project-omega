import build
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('rule')
    parser.add_argument('--parallel', action='store_true')
    parser.add_argument("--watch", action='store_true')
    args = parser.parse_args()

    BuildGraph = build.Graph()
    BuildGraph.create_graph()
    BuildGraph.detect_circular_dependency(args.rule)

    if args.parallel:
        Executor = build.ParallelExe(BuildGraph.rule_name_to_rule)
        Executor.exe(args.rule)
    else:
        Executor = build.SerialExe(BuildGraph.rule_name_to_rule)
        Executor.exe(args.rule)
    if args.watch:
        Watch = build.WatchChanges(Executor)
        Watch.map_file_command(args.rule)
        Watch.watch_init()
