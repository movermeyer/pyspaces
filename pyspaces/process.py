#!/usr/bin/env python
# coding=utf-8
"""This is part of [pyspaces](https://github.com/Friz-zy/pyspaces)

License: MIT or BSD or Apache 2.0
Copyright (c) 2014 Filipp Kucheryavy aka Frizzy <filipp.s.frizzy@gmail.com>

"""


from os import chroot
from .setns import setns
from . import cloning as cl
from multiprocessing import Process
from .args_aliases import na, ca, pop, pop_all


class Container(Process):
    """Class wrapper over `multiprocessing.Process`.

    Container objects represent activity that is run in a separate process.

    The class is analagous to `threading.Thread`.

    """
    _Popen = cl.Clone

    def __init__(self, *args, **kwargs):
        """Set clone flags and execute Process.__init__

        Args:
          *args (list): arguments for Process.__init__
          **kwargs (dict): arguments for Process.__init__
          flags (int): flags for clone, default is 0
          uid_map (str): UID mapping for new namespace,
            default is ""
          gid_map (str): GID mapping for new namespace,
            default is ""
          map_zero (bool): Map user's UID and GID to 0
            in user namespace, default is False
          all (bool): set all 6 namespaces,
            default is False
          vm (bool): set CLONE_VM flag,
            default is False
          fs (bool): set CLONE_FS flag,
            default is False
          files (bool): set CLONE_FILES flag,
            default is False
          sighand (bool): set CLONE_SIGHAND flag,
            default is False
          ptrace (bool): set CLONE_PTRACE flag,
            default is False
          vfork (bool): set CLONE_VFORK flag,
            default is False
          parent (bool): set CLONE_PARENT flag,
            default is False
          thread (bool): set CLONE_THREAD flag,
            default is False
          newns (bool): set CLONE_NEWNS flag,
            default is False
          sysvsem (bool): set CLONE_SYSVSEM flag,
            default is False
          settls (bool): set CLONE_SETTLS flag,
            default is False
          settid (bool): set CLONE_PARENT_SETTID flag,
            default is False
          child_cleartid (bool): set CLONE_CHILD_CLEARTID flag,
            default is False
          detached (bool): set CLONE_DETACHED flag,
            default is False
          untraced (bool): set CLONE_UNTRACED flag,
            default is False
          child_settid (bool): set CLONE_CHILD_SETTID flag,
            default is False
          newuts (bool): set CLONE_NEWUTS flag,
            default is False
          newipc (bool): set CLONE_NEWIPC flag,
            default is False
          newuser (bool): set CLONE_NEWUSER flag,
            default is False
          newpid (bool): set CLONE_NEWPID flag,
            default is False
          newnet (bool): set CLONE_NEWNET flag,
            default is False
          io (bool): set CLONE_IO flag,
            default is False

        """
        self.clone_flags = kwargs.pop('flags', 0)
        self.uid_map = kwargs.pop('uid_map', "")
        self.gid_map = kwargs.pop('gid_map', "")
        self.map_zero = kwargs.pop('map_zero', False)

        if kwargs.pop('all', False):
            kwargs['newipc'] = True
            kwargs['newns'] = True
            kwargs['newnet'] = True
            kwargs['newpid'] = True
            kwargs['newuser'] = True
            kwargs['newuts'] = True
        if kwargs.pop('vm', False):
            self.clone_flags |= cl.CLONE_VM
        if kwargs.pop('fs', False):
            self.clone_flags |= cl.CLONE_FS
        if kwargs.pop('files', False):
            self.clone_flags |= cl.CLONE_FILES
        if kwargs.pop('sighand', False):
            self.clone_flags |= cl.CLONE_SIGHAND
        if kwargs.pop('ptrace', False):
            self.clone_flags |= cl.CLONE_PTRACE
        if kwargs.pop('vfork', False):
            self.clone_flags |= cl.CLONE_VFORK
        if kwargs.pop('parent', False):
            self.clone_flags |= cl.CLONE_PARENT
        if kwargs.pop('thread', False):
            self.clone_flags |= cl.CLONE_THREAD
        if kwargs.pop('newns', False):
            self.clone_flags |= cl.CLONE_NEWNS
        if kwargs.pop('sysvsem', False):
            self.clone_flags |= cl.CLONE_SYSVSEM
        if kwargs.pop('settls', False):
            self.clone_flags |= cl.CLONE_SETTLS
        if kwargs.pop('settid', False):
            self.clone_flags |= cl.CLONE_PARENT_SETTID
        if kwargs.pop('child_cleartid', False):
            self.clone_flags |= cl.CLONE_CHILD_CLEARTID
        if kwargs.pop('detached', False):
            self.clone_flags |= cl.CLONE_DETACHED
        if kwargs.pop('untraced', False):
            self.clone_flags |= cl.CLONE_UNTRACED
        if kwargs.pop('child_settid', False):
            self.clone_flags |= cl.CLONE_CHILD_SETTID
        if kwargs.pop('newuts', False):
            self.clone_flags |= cl.CLONE_NEWUTS
        if kwargs.pop('newipc', False):
            self.clone_flags |= cl.CLONE_NEWIPC
        if kwargs.pop('newuser', False):
            self.clone_flags |= cl.CLONE_NEWUSER
        if kwargs.pop('newpid', False):
            self.clone_flags |= cl.CLONE_NEWPID
        if kwargs.pop('newnet', False):
            self.clone_flags |= cl.CLONE_NEWNET
        if kwargs.pop('io', False):
            self.clone_flags |= cl.CLONE_IO

        Process.__init__(self, *args, **kwargs)

class Chroot(Container):
    """Class wrapper over `pyspaces.Container`.

    Chroot objects represent activity that is run in a separate process
    in new filesystem and user namespaces.

    The class is analagous to `threading.Thread`.

    """
    def __init__(self, path, target, args=(), kwargs={}, *cargs, **ckwargs):
        """Set target and clone flags and execute Container.__init__

        Set newuser and newns clone flags, set self.chroot
        as target with necessary args and kwargs. Then
        execute Container.__init__ with updated parameters.

        Note:
          If the program you're trying to exec is dynamic
          linked, and the dynamic linker is not present in /lib
          in the chroot environment - you would get the
          "OSError: [Errno 2] No such file or directory" error.
          You'd need all the other files the dynamic-linked
          program depends on, including shared libraries and
          any essential configuration/table/etc in the new
          root directories.
          [src](http://www.ciiycode.com/0JiJzPgggqPg/why-doesnt-exec-work-after-chroot)

        Args:
          path (str): path to chroot new root
          target (python function): python function
            for executing after chroot
          args (list): args for target,
            default is ()
          kwargs (dict): kwargs for target,
            default is {}
          *cargs (list): arguments for Container.__init__
          **ckwargs (dict): arguments for Container.__init__

        """
        ckwargs['args'] = ()
        ckwargs['kwargs'] = {
            'path': path, 'target': target,
            'args': args, 'kwargs': kwargs
        }
        ckwargs['target'] = self.chroot
        ckwargs['newuser'] = True
        ckwargs['newns'] = True
        Container.__init__(self, *cargs, **ckwargs)

    def chroot(self, path, target, args=(), kwargs={}):
        """Change root and execute target.

        Change root with os.chroot. Then execute
        target with args and kwargs.

        Args:
          path (str): path to chroot new root
          target (python function): python function
            for executing after chroot
          args (list): args for target,
            default is ()
          kwargs (dict): kwargs for target,
            default is {}

        """
        chroot(path)
        return target(*args, **kwargs)

class Inject(Container):
    """Class wrapper over `multiprocessing.Process`.

    Create process in namespaces of another one.

    The class is analagous to `threading.Thread`.

    """
    def __init__(self, target_pid, target, args=(), kwargs={}, proc='/proc', *pargs, **pkwargs):
        """Set new namespaces and execute Process.__init__

        Set self.setns as target with necessary args and kwargs.
        Then execute Process.__init__ with updated parameters.


        Args:
          pid (str or int): pid of target process
          target (python function): python function
            for executing
          args (list): args for target,
            default is ()
          kwargs (dict): kwargs for target,
            default is {}
          proc (str): root directory of proc fs,
            default is '/proc'
          *pargs (list): arguments for Container.__init__
          **pkwargs (dict): arguments for Container.__init__

        In args or kwargs expected one or many of
        many keys for setns:
        'all', 'ipc', 'newipc', 'mnt', 'newns',
        'net', 'newnet', 'pid', 'newpid',
        'user', 'newuser', 'uts', 'newuts'.
        If no one of them submitted 'all' will
        be used.

        """
        nspaces = []
        # all as default
        if 'all' in pargs or ('all' in pkwargs and pkwargs['all']):
            nspaces.append('all')
        for ns in na:
            for a in na[ns]['aliases']:
                if a in args or (a in pkwargs and pkwargs[a]):
                    nspaces.append(ns)

        pkwargs['args'] = ()
        pkwargs['kwargs'] = {
            'pid': target_pid, 'target': target,
            'args': args, 'kwargs': kwargs,
            'nspaces': nspaces, 'proc': proc,
        }
        pkwargs['target'] = self.setns
        Container.__init__(self, *pargs, **pkwargs)

    def setns(self, pid, target, args=(), kwargs={}, nspaces=[], proc='/proc'):
        """Change namespaces and execute target.

        Args:
          path (str): path to chroot new root
          target (python function): python function
            for executing after chroot
          args (list): args for target,
            default is ()
          kwargs (dict): kwargs for target,
            default is {}
          nspaces (list): list of namespaces for setns
          proc (str): root directory of proc fs,
            default is '/proc'

        """
        with setns(pid, proc, *nspaces):
            return target(*args, **kwargs)
