/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { onWillStart, useState } from "@odoo/owl";

export class VisaFinanceListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            income: 0,
            expense: 0,
            profit: 0,
            count: 0,
            debt: 0,
        });

        onWillStart(async () => {
            await this._loadSummary();
        });
    }

    async _loadSummary() {
        const domain = this.model?.root?.domain || [];
        const res = await this.orm.call(
            "visa.finance",
            "get_finance_summary",
            [domain],
            {
                context: this.model?.root?.context || {},
            }
        );

        this.state.income = this._formatCurrency(res?.income || 0);
        this.state.expense = this._formatCurrency(res?.expense || 0);
        this.state.profit = this._formatCurrency(res?.profit || 0);
        this.state.count = res?.lead_count || 0;
        this.state.debt = this._formatCurrency(res?.debt_sum || 0);
    }

    _formatCurrency(value) {
        return new Intl.NumberFormat("uz-UZ", {
            style: "decimal",
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    }

    async onSearch(domain) {
        await super.onSearch(domain);
        await this._loadSummary();
    }

    async _applyExtraDomain(extraDomain) {
        const current = this.model?.root?.domain || [];
        await this.model.load({ domain: current.concat(extraDomain) });
        await this._loadSummary();
    }

    /**
     * Get filtered CRM lead IDs based on current finance records
     */
    async _getFilteredLeadIds() {
        const domain = this.model?.root?.domain || [];
        const context = this.model?.root?.context || {};
        
        // Get all finance records matching current filters
        const financeRecords = await this.orm.searchRead(
            "visa.finance",
            domain,
            ["crm_lead_id"],
            { context }
        );

        // Get company filtering
        const companyIds = context.allowed_company_ids || [];

        // Extract unique lead IDs
        const leadIds = new Set();
        for (const record of financeRecords) {
            if (record.crm_lead_id && record.crm_lead_id[0]) {
                leadIds.add(record.crm_lead_id[0]);
            }
        }

        // Apply the same filtering logic as get_finance_summary
        if (leadIds.size > 0) {
            const leads = await this.orm.searchRead(
                "crm.lead",
                [
                    ["id", "in", Array.from(leadIds)],
                    ["active", "=", true],
                    ["stage_id", "!=", 1],
                    ["lost_reason_id", "=", false],
                    "|",
                    ["company_id", "=", false],
                    ["company_id", "in", companyIds],
                ],
                ["id"],
                { context }
            );

            return leads.map(l => l.id);
        }

        return [];
    }

    /**
     * Open CRM leads with current filters
     */
    async _openCrmLeads(title) {
        const leadIds = await this._getFilteredLeadIds();
        
        this.action.doAction({
            type: "ir.actions.act_window",
            name: title,
            res_model: "crm.lead",
            views: [
                [false, "kanban"],
                [false, "list"],
                [false, "form"]
            ],
            domain: [["id", "in", leadIds]],
            context: {
                ...this.model?.root?.context || {},
            },
        });
    }

    async onClickIncome() {
        await this._openCrmLeads("CRM Leads - Kirim");
    }

    async onClickExpense() {
        await this._openCrmLeads("CRM Leads - Chiqim");
    }

    async onClickProfit() {
        await this._openCrmLeads("CRM Leads - Foyda");
    }

    async onClickCount() {
        await this._openCrmLeads("CRM Leads - Visa Soni");
    }

    async onClickDebt() {
        const leadIds = await this._getFilteredLeadIds();
        
        // Filter to show only leads with remaining amount > 0
        if (leadIds.length > 0) {
            const leadsWithDebt = await this.orm.searchRead(
                "crm.lead",
                [
                    ["id", "in", leadIds],
                    ["remaining_amount", ">", 0],
                ],
                ["id"],
                { context: this.model?.root?.context || {} }
            );

            this.action.doAction({
                type: "ir.actions.act_window",
                name: "CRM Leads - Qarz",
                res_model: "crm.lead",
                views: [
                    [false, "kanban"],
                    [false, "list"],
                    [false, "form"]
                ],
                domain: [["id", "in", leadsWithDebt.map(l => l.id)]],
                context: {
                    ...this.model?.root?.context || {},
                },
            });
        }
    }
}

export const VisaFinanceListView = {
    ...listView,
    Controller: VisaFinanceListController,
    buttonTemplate: "visa_finance.VisaFinanceListButtonsRoot",
};

registry.category("views").add("visa_finance_list", VisaFinanceListView);