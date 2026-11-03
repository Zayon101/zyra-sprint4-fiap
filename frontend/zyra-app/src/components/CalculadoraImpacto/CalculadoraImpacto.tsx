import { useState, type FormEvent } from 'react';
import CardResultadoCalculo from '../CardResultadoCalculo/CardResultadoCalculo';

const FATOR_CARRO_KG_KM = 0.12;
const FATOR_METRO_KG_KM = 0.006;

type ResultadoCalculo = {
    carro: number;
    metro: number;
    evitado: number;
};

function formatarKg(valor: number): string {
    return valor.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

export default function CalculadoraImpacto() {
    const [km, setKm] = useState('');
    const [resultado, setResultado] = useState<ResultadoCalculo | null>(null);

    function calcularImpacto(evento: FormEvent<HTMLFormElement>) {
        evento.preventDefault();

        const quilometros = Number(km);

        if (!quilometros || quilometros <= 0) {
            return;
        }

        setResultado({
            carro: quilometros * FATOR_CARRO_KG_KM,
            metro: quilometros * FATOR_METRO_KG_KM,
            evitado: quilometros * (FATOR_CARRO_KG_KM - FATOR_METRO_KG_KM),
        });
    }

    return (
        <div className="card-shape-alt mx-auto max-w-[80rem] bg-card-dark-green p-[4rem_4.8rem] shadow-[0_4px_24px_rgba(60,88,74,0.18)]">
            <h3 className="mb-[0.8rem] flex items-center justify-center gap-[1rem] font-text text-[2rem] font-bold text-text-light-yellow">
                <i className="fa-solid fa-leaf" aria-hidden="true" />
                Quanto CO₂ você evitou hoje?
            </h3>
            <p className="mb-[3.2rem] text-center font-text text-[1.4rem] leading-[1.6] text-card-green">
                Compare a emissão de CO₂ entre andar de carro e de metrô/trem.
                <br />
                Descubra o impacto real da sua escolha sustentável.
            </p>

            <form
                onSubmit={calcularImpacto}
                className="mb-[3.2rem] flex flex-wrap items-center justify-center gap-[1.2rem]"
            >
                <label className="font-text text-[1.5rem] font-bold text-text-light-yellow" htmlFor="calc-km">
                    Quilômetros percorridos:
                </label>
                <input
                    id="calc-km"
                    type="number"
                    min={1}
                    max={999}
                    placeholder="0"
                    value={km}
                    onChange={(evento) => setKm(evento.target.value)}
                    aria-label="Quilômetros percorridos"
                    className="w-[10rem] rounded-[0.8rem] border-2 border-card-green bg-[rgba(255,255,255,0.08)] p-[1rem_1.4rem] text-center font-text text-[1.8rem] font-bold text-text-light-yellow outline-none transition-colors duration-200 [appearance:textfield] focus:border-text-light-yellow [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                />
                <span className="font-text text-[1.5rem] text-card-green">km</span>
                <button
                    type="submit"
                    aria-label="Calcular impacto ambiental"
                    className="rounded-[0.8rem] bg-button-pink p-[1rem_2.8rem] font-text text-[1.5rem] font-semibold text-white shadow-[0_2px_8px_rgba(154,74,97,0.3)] transition-[transform,box-shadow] duration-200 hover:scale-105 hover:shadow-[0_6px_20px_rgba(154,74,97,0.4)]"
                >
                    Calcular
                </button>
            </form>

            <div aria-live="polite" className="mb-[2.4rem] flex flex-wrap justify-center gap-[1.6rem]">
                <CardResultadoCalculo
                    icone="fa-solid fa-car"
                    label="De carro"
                    valor={resultado ? formatarKg(resultado.carro) : null}
                />
                <CardResultadoCalculo
                    icone="fa-solid fa-train-subway"
                    label="De metrô"
                    valor={resultado ? formatarKg(resultado.metro) : null}
                />
                <CardResultadoCalculo
                    icone="fa-solid fa-circle-check"
                    label="CO₂ evitado"
                    valor={resultado ? formatarKg(resultado.evitado) : null}
                    destaque
                />
            </div>

            {resultado && (
                <p
                    aria-live="polite"
                    className="rounded-[0.8rem] bg-[rgba(255,255,255,0.06)] p-[1.6rem_2rem] text-center font-text text-[1.4rem] leading-[1.7] text-card-green"
                >
                    Ao percorrer <strong className="font-bold text-text-light-yellow">{km} km</strong> de metrô em vez
                    de carro, você evitou{' '}
                    <strong className="font-bold text-text-light-yellow">
                        {formatarKg(resultado.evitado)} kg de CO₂
                    </strong>
                    . <i className="fa-solid fa-leaf" aria-hidden="true" />
                </p>
            )}
        </div>
    );
}
