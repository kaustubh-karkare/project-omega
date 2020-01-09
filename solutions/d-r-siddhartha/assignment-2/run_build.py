import build
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('rule')
    parser.add_argument('--parallel', action='store_true')
    parser.add_argument("--watch", action='store_true')
    args = parser.parse_args()

    build_tool_graph = build.Graph()
    build_tool_graph.create_graph()
    build_tool_graph.detect_circular_dependency(args.rule)

    if args.parallel:
        executor = build.ParallelExe(build_tool_graph)
        executor.exe(args.rule)
    else:
        executor = build.SerialExe(build_tool_graph)
        executor.exe(args.rule)
    if args.watch:
        watch = build.WatchChanges(executor)
        watch.map_file_command(args.rule)
        watch.watch_changes()
