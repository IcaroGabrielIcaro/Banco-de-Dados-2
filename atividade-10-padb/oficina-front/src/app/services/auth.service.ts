import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Usuario } from '../models/usuario';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://localhost:8000/api/auth';
  private readonly _httpClient = inject(HttpClient);

  registrar(usuario: Usuario): Observable<any> {
    return this._httpClient.post(`${this.apiUrl}/registro/`, usuario);
  }

  login(data: { email: string; password: string }): Observable<any> {
    return this._httpClient.post(`${this.apiUrl}/login/`, data);
  }

  logout(token: string): Observable<any> {
    return this._httpClient.post(`${this.apiUrl}/logout/`, {}, {
      headers: { Authorization: `Token ${token}` }
    });
  }
}
