import { Component, inject } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Usuario } from '../../models/usuario';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-cadastro',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './cadastro.component.html'
})
export class CadastroComponent {
    readonly _usuarioService = inject(AuthService);

    usuarioForm: FormGroup = new FormGroup({
        username: new FormControl('', [Validators.required]),
        email: new FormControl('', [Validators.required, Validators.email]),
        cpf: new FormControl('', [Validators.required]),
        telefone: new FormControl(''),
        tipo_perfil: new FormControl('', [Validators.required]),
        password: new FormControl('', [Validators.required, Validators.minLength(6)])
    });

  registrar() {
    if (this.usuarioForm.invalid) {
      console.log("FORM INVÁLIDO");
      console.log(this.usuarioForm.errors);
      console.log(this.usuarioForm);
      console.log("VALORES:", this.usuarioForm.value);
      console.log("CONTROLES:", Object.fromEntries(
        Object.entries(this.usuarioForm.controls).map(([k, v]) => [k, v.errors])
      ));

      this.usuarioForm.markAllAsTouched();
      return;
    }

    console.log('Formulário válido, enviando dados:', this.usuarioForm.value);

    this._usuarioService.registrar(this.usuarioForm.value as Usuario).subscribe({
      next: res => {
        console.log('Registrado:', res);
        alert('Cadastro realizado com sucesso!');
        this.usuarioForm.reset();
      },
      error: err => {
        console.error(err);
        alert('Erro ao realizar cadastro. Tente novamente.');
      }
    });
  }
}
