import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import type { DadosContato, StatusEnvio } from '../../types/contato';
import CampoTexto from '../CampoTexto/CampoTexto';
import CampoTextarea from '../CampoTextarea/CampoTextarea';
import MensagemRetorno from '../MensagemRetorno/MensagemRetorno';

const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const REGEX_TELEFONE = /^\(\d{2}\)\s?\d{4,5}-\d{4}$/;

export default function FormularioContato() {
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<DadosContato>();

    const [status, setStatus] = useState<StatusEnvio>(null);

    useEffect(() => {
        if (status === null) return;

        const temporizador = setTimeout(() => setStatus(null), 5000);
        return () => clearTimeout(temporizador);
    }, [status]);

    async function aoEnviar(dados: DadosContato) {
        try {
            // Esta sprint não consome API: o envio é simulado.
            await new Promise((resolve) => setTimeout(resolve, 800));
            console.log('Dados enviados pelo formulário de contato:', dados);
            setStatus('sucesso');
            reset();
        } catch {
            setStatus('erro');
        }
    }

    return (
        <>
            {status && (
                <MensagemRetorno
                    tipo={status}
                    texto={
                        status === 'sucesso'
                            ? 'Mensagem enviada com sucesso! Em breve entraremos em contato.'
                            : 'Não foi possível enviar sua mensagem. Tente novamente.'
                    }
                />
            )}

            <form noValidate onSubmit={handleSubmit(aoEnviar)} className="flex flex-col gap-[2.4rem] mobile-lg:gap-[2.8rem] tablet:gap-[3.2rem]">
                <div className="grid grid-cols-1 gap-[2rem] tablet:grid-cols-2 tablet:gap-[2.4rem]">
                    <CampoTexto
                        id="contato-nome"
                        label="Nome"
                        placeholder="Digite seu nome"
                        autoComplete="given-name"
                        register={register('nome', {
                            required: 'Informe seu nome.',
                            minLength: { value: 2, message: 'Use pelo menos 2 caracteres.' },
                        })}
                        erro={errors.nome?.message}
                    />
                    <CampoTexto
                        id="contato-sobrenome"
                        label="Sobrenome"
                        placeholder="Digite seu sobrenome"
                        autoComplete="family-name"
                        register={register('sobrenome', {
                            required: 'Informe seu sobrenome.',
                            minLength: { value: 2, message: 'Use pelo menos 2 caracteres.' },
                        })}
                        erro={errors.sobrenome?.message}
                    />
                </div>

                <div className="grid grid-cols-1 gap-[2rem] tablet:grid-cols-2 tablet:gap-[2.4rem]">
                    <CampoTexto
                        id="contato-email"
                        label="Email"
                        type="email"
                        placeholder="Digite seu Email"
                        autoComplete="email"
                        register={register('email', {
                            required: 'Informe seu e-mail.',
                            pattern: { value: REGEX_EMAIL, message: 'Informe um e-mail válido.' },
                        })}
                        erro={errors.email?.message}
                    />
                    <CampoTexto
                        id="contato-telefone"
                        label="Telefone"
                        type="tel"
                        placeholder="(11) 91234-5678"
                        autoComplete="tel"
                        register={register('telefone', {
                            required: 'Informe seu telefone.',
                            pattern: { value: REGEX_TELEFONE, message: 'Use o formato (11) 91234-5678.' },
                        })}
                        erro={errors.telefone?.message}
                    />
                </div>

                <CampoTextarea
                    id="contato-mensagem"
                    label="Mensagem"
                    placeholder="Eu gostaria de saber mais sobre..."
                    rows={6}
                    register={register('mensagem', {
                        required: 'Escreva sua mensagem.',
                        minLength: { value: 10, message: 'Use pelo menos 10 caracteres.' },
                    })}
                    erro={errors.mensagem?.message}
                />

                <hr className="h-[1.5px] border-none bg-separator-light" aria-hidden="true" />

                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="block w-full rounded-[0.8rem] bg-card-green px-[2.4rem] py-[1.3rem] text-center font-text text-[1.5rem] font-semibold text-title mobile-lg:px-[3rem] mobile-lg:py-[1.4rem] mobile-lg:text-[1.6rem] tablet:px-[3.6rem] tablet:py-[1.5rem] shadow-[0_2px_8px_rgba(60,88,74,0.18)] transition-[background-color,transform,box-shadow] duration-300 hover:scale-[1.02] hover:bg-card-dark-green hover:text-text-light-yellow hover:shadow-[0_6px_20px_rgba(60,88,74,0.28)] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-70"
                >
                    {isSubmitting ? 'Enviando...' : 'Enviar'}
                </button>
            </form>
        </>
    );
}
