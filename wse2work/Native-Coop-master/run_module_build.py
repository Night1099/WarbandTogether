"""Run the full module build; stop at the first failing step.

Several legacy process_*.py steps print ERROR and exit 0, so the exit code
alone cannot gate a deploy. Any step whose output contains an ERROR line or
a Python traceback fails the build. Python 2.7 (the module system).
"""
from __future__ import print_function
import glob
import os
import re
import subprocess
import sys

STEPS = [
    'process_init', 'process_global_variables', 'process_strings',
    'process_skills', 'process_music', 'process_animations', 'process_meshes',
    'process_sounds', 'process_skins', 'process_map_icons', 'process_factions',
    'process_items', 'process_scenes', 'process_troops', 'process_particle_sys',
    'process_scene_props', 'process_tableau_materials', 'process_presentations',
    'process_party_tmps', 'process_parties', 'process_quests', 'process_info_pages',
    'process_scripts', 'process_mission_tmps', 'process_game_menus',
    'process_simple_triggers', 'process_dialogs', 'process_global_variables_unused',
    'process_postfx',
]

FAILURE_RE = re.compile(r'(?im)^\s*(?:ERROR\b|Traceback \(most recent call last\))')


def run_step(step):
    proc = subprocess.Popen([sys.executable, '-B', step + '.py'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    raw, _ = proc.communicate()
    output = raw.decode('utf-8', 'replace')
    sys.stdout.write(output.encode('ascii', 'replace').decode('ascii'))
    return proc.returncode == 0 and not FAILURE_RE.search(output)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for step in STEPS:
        if not run_step(step):
            print('BUILD FAILED in %s -- do not deploy this partial export.' % step)
            return 1
    for pyc in glob.glob('*.pyc'):
        os.remove(pyc)
    print('Full module build succeeded (%d steps).' % len(STEPS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
