type TituloErroProps = {
    codigo: string;
};

export default function TituloErro({ codigo }: TituloErroProps) {
    return (
<div className="flex flex-col items-center">
    <span
        aria-hidden="true"
        className="font-title text-[6rem] font-black leading-none text-brand mobile-lg:text-[7.5rem] tablet:text-[9.5rem] desktop:text-[11rem]"
    >
        {codigo}
    </span>
</div>
    );
}
