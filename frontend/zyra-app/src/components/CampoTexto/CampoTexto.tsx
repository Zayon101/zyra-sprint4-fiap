import type { UseFormRegisterReturn } from 'react-hook-form';

type CampoTextoProps = {
    id: string;
    label: string;
    type?: 'text' | 'email' | 'tel';
    placeholder?: string;
    autoComplete?: string;
    register: UseFormRegisterReturn;
    erro?: string;
};

export default function CampoTexto({
    id,
    label,
    type = 'text',
    placeholder,
    autoComplete,
    register,
    erro,
}: CampoTextoProps) {
    const idErro = `erro-${id}`;

    return (
        <div className="flex flex-col gap-[0.8rem]">
            <label htmlFor={id} className="font-text text-[1.5rem] font-medium text-title">
                {label}
            </label>
            <input
                id={id}
                type={type}
                placeholder={placeholder}
                autoComplete={autoComplete}
                aria-invalid={Boolean(erro)}
                aria-describedby={erro ? idErro : undefined}
                className={`w-full rounded-[10rem] border-[1.5px] bg-transparent px-[2rem] py-[1.2rem] font-text text-[1.4rem] text-text-dark outline-none transition-[border-color,box-shadow] duration-[250ms] placeholder:text-separator-light focus:border-nav focus:shadow-[0_0_0_3px_rgba(60,88,74,0.12)] ${
                    erro ? 'border-[#c0392b] shadow-[0_0_0_3px_rgba(192,57,43,0.12)]' : 'border-separator-dark'
                }`}
                {...register}
            />
            <small id={idErro} role="alert" className="min-h-[1.6rem] font-text text-[1.2rem] text-[#c0392b]">
                {erro}
            </small>
        </div>
    );
}
