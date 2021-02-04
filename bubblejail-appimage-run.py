#!/usr/bin/python3 -I
from argparse import ArgumentParser
from asyncio import create_subprocess_exec, get_event_loop, run, wait_for
from asyncio.subprocess import DEVNULL, PIPE

loop = get_event_loop()


async def run_bubblejail(mount_point: str, instance_name: str) -> None:
    bubblejail_subprocess = await create_subprocess_exec(
        '/usr/bin/env', f'BUBBLEJAIL_DEBUG_ROOT_SHARE={mount_point}',
        'python3', '-X', 'dev', './dev.py',  # change to 'bubblejail'
        'run', instance_name, mount_point + '/AppRun',
    )
    await bubblejail_subprocess.communicate()


async def startup(appimage_path: str, instance_name: str) -> None:
    mount_subprocess = await create_subprocess_exec(
        appimage_path, '--appimage-mount', appimage_path,
        stdin=DEVNULL, stdout=PIPE,
    )

    assert mount_subprocess.stdout is not None

    mount_point_bytes: bytes = await wait_for(
        mount_subprocess.stdout.readline(),
        timeout=1)

    assert mount_point_bytes

    mount_point = mount_point_bytes.decode('utf-8')[:-1]

    try:
        await run_bubblejail(mount_point, instance_name)
    finally:
        mount_subprocess.terminate()
        await mount_subprocess.communicate()


def main() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument('appimage_path')
    arg_parser.add_argument('bubblejail_instance')
    namespace = arg_parser.parse_args()
    run(startup(namespace.appimage_path, namespace.bubblejail_instance))


if __name__ == '__main__':
    main()
