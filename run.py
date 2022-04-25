from streamlit import bootstrap

real_script = 'view/mercado_energia_GUI.py'

bootstrap.run(real_script, f'run.py {real_script}', [], {})