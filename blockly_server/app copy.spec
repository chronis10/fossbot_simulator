# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('utils', 'utils'), ('static', 'static'), ('lib', 'lib')],
    hiddenimports=[
        'engineio.async_drivers.threading',
                'eventlet.hubs.epolls',
                'eventlet.hubs.kqueue',
                'eventlet.hubs.selects',
                'eventlet',
                'dns.dnssec',
                'dns.asyncbackend',
                'dns.asyncquery',
                'dns.asyncresolver',
                'dns.versioned',
                'dns.e164',
                'dns.namedict',
                'dns.tsigkeyring' ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FossBot Blockly',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='app.app',
    icon="app.ico",
    bundle_identifier=None,
)