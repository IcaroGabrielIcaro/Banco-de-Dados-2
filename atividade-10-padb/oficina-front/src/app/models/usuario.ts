export interface Usuario {
  username: string;
  email: string;
  cpf: string;
  telefone?: string;
  tipo_perfil: string;
  password?: string;
}