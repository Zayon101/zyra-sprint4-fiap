import type { UseFormRegisterReturn } from 'react-hook-form';

type CampoTextareaProps = {
    id: string;
    label: string;
    placeholder?: string;
    rows?: number;
    register: UseFormRegisterReturn;
    erro?: string;
};

export default function CampoTextarea({ id, label, placeholder, rows = 6, register, erro }: CampoTextareaProps) {
    const idErro = `erro-${id}`;

    return (
        <div className="flex flex-col gap-[0.8rem]">
            <label htmlFor={id} className="font-text text-[1.5rem] font-medium text-title">
                {label}
            </label>
            <textarea
                id={id}
                rows={rows}
                placeholder={placeholder}
                aria-invalid={Boolean(erro)}
                aria-describedby={erro ? idErro : undefined}
                className={`min-h-[14rem] w-full resize-y rounded-[1.2rem] border-[1.5px] bg-transparent px-[2rem] py-[1.2rem] font-text text-[1.4rem] leading-[1.6] text-text-dark outline-none transition-[border-color,box-shadow] duration-[250ms] placeholder:text-separator-light focus:border-nav focus:shadow-[0_0_0_3px_rgba(60,88,74,0.12)] ${
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
